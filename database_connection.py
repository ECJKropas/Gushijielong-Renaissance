import os
import time
import logging
from typing import Optional, Callable, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DatabaseError
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)

# 数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 连接重试配置
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2
CONNECTION_TIMEOUT = 10

# 数据库状态
class DatabaseStatus:
    def __init__(self):
        self.is_available = True
        self.last_check_time = 0
        self.check_interval = 30  # 30秒检查一次
        self.connection_error_count = 0
        self.last_error_time = None
        
    def should_check_connection(self) -> bool:
        """检查是否应该验证数据库连接"""
        current_time = time.time()
        return current_time - self.last_check_time > self.check_interval
        
    def mark_connection_error(self):
        """标记连接错误"""
        self.is_available = False
        self.connection_error_count += 1
        self.last_error_time = time.time()
        
    def mark_connection_success(self):
        """标记连接成功"""
        self.is_available = True
        self.connection_error_count = 0
        self.last_check_time = time.time()

db_status = DatabaseStatus()

class DatabaseConnectionManager:
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.session_maker: Optional[sessionmaker] = None
        self._initialize_connection()
        
    def _build_database_url(self) -> str:
        """构建数据库连接URL"""
        return f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
        
    def _initialize_connection(self):
        """初始化数据库连接"""
        try:
            database_url = self._build_database_url()
            
            # 创建引擎配置
            engine_kwargs = {
                'echo': False,  # 关闭SQL日志
                'pool_pre_ping': True,  # 连接前检查
                'pool_recycle': 3600,  # 连接回收时间
                'pool_size': 5,  # 连接池大小
                'max_overflow': 10,  # 最大溢出连接
                'connect_args': {
                    'charset': 'utf8mb4',
                    'connect_timeout': CONNECTION_TIMEOUT,
                    'read_timeout': 30,
                    'write_timeout': 30,
                    'ssl_ca': None,
                }
            }
            
            self.engine = create_engine(database_url, **engine_kwargs)
            self.session_maker = sessionmaker(bind=self.engine)
            
            # 测试连接
            self._test_connection()
            db_status.mark_connection_success()
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error(f"数据库连接初始化失败: {str(e)}")
            db_status.mark_connection_error()
            raise
            
    def _test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False
            
    def reconnect(self) -> bool:
        """尝试重新连接数据库"""
        logger.info("尝试重新连接数据库...")
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                logger.info(f"重连尝试 {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
                
                # 关闭现有连接
                if self.engine:
                    self.engine.dispose()
                    
                # 重新初始化连接
                self._initialize_connection()
                
                logger.info("数据库重连成功")
                db_status.mark_connection_success()
                return True
                
            except Exception as e:
                logger.error(f"重连尝试 {attempt + 1} 失败: {str(e)}")
                
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
                    
        logger.error("数据库重连失败，已达到最大重试次数")
        db_status.mark_connection_error()
        return False
        
    def is_connection_available(self) -> bool:
        """检查数据库连接是否可用"""
        if not db_status.should_check_connection():
            return db_status.is_available
            
        try:
            if self.engine and self._test_connection():
                db_status.mark_connection_success()
                return True
            else:
                db_status.mark_connection_error()
                return False
        except Exception:
            db_status.mark_connection_error()
            return False
            
    def get_session(self) -> Optional[Session]:
        """获取数据库会话"""
        if not self.is_connection_available():
            logger.warning("数据库连接不可用，尝试重连...")
            if not self.reconnect():
                return None
                
        try:
            return self.session_maker()
        except Exception as e:
            logger.error(f"创建数据库会话失败: {str(e)}")
            return None
            
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """执行带重试的数据库操作"""
        last_exception = None
        
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                session = self.get_session()
                if session is None:
                    raise Exception("无法获取数据库会话")
                    
                result = func(session, *args, **kwargs)
                session.close()
                return result
                
            except (OperationalError, DatabaseError) as e:
                last_exception = e
                logger.error(f"数据库操作失败 (尝试 {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {str(e)}")
                
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    if not self.reconnect():
                        break
                    time.sleep(RETRY_DELAY_SECONDS)
                
            except Exception as e:
                logger.error(f"非数据库错误: {str(e)}")
                raise
                
        raise last_exception or Exception("数据库操作失败，已达到最大重试次数")

# 创建全局连接管理器实例
db_manager = DatabaseConnectionManager()

@contextmanager
def get_db_session():
    """获取数据库会话的上下文管理器"""
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        if session:
            session.rollback()
        logger.error(f"数据库会话错误: {str(e)}")
        raise
    finally:
        if session:
            session.close()