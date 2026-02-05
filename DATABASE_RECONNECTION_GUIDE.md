# 数据库重连机制与临时本地存储方案

## 概述

本项目实现了增强的数据库连接管理机制，包括自动重连、临时本地存储回退、健康检查等功能，确保在数据库连接不稳定或不可用时，应用仍能保持基本功能运行。

## 核心组件

### 1. 数据库连接管理器 (`database_connection.py`)

#### 功能特性
- **连接池管理**: 使用SQLAlchemy连接池，支持连接复用和超时控制
- **自动重连**: 当检测到连接失败时，自动尝试重新连接
- **连接健康检查**: 定期检查数据库连接状态
- **重试机制**: 支持可配置的重试次数和间隔时间

#### 主要类和方法

```python
class DatabaseConnectionManager:
    def __init__(self):
        # 初始化数据库连接
        
    def reconnect(self) -> bool:
        # 尝试重新连接数据库
        
    def is_connection_available(self) -> bool:
        # 检查数据库连接是否可用
        
    def execute_with_retry(self, func, *args, **kwargs):
        # 执行带重试的数据库操作
```

#### 配置参数
- `MAX_RETRY_ATTEMPTS = 3`: 最大重试次数
- `RETRY_DELAY_SECONDS = 2`: 重试间隔时间
- `CONNECTION_TIMEOUT = 10`: 连接超时时间
- `DB_CHECK_INTERVAL = 30`: 连接检查间隔

### 2. 临时本地存储 (`temp_storage.py`)

#### 功能特性
- **数据持久化**: 将数据保存到本地JSON文件
- **修改跟踪**: 跟踪数据的增删改操作
- **自动清理**: 定期清理过期的临时数据
- **线程安全**: 支持多线程并发访问

#### 主要类和方法

```python
class TemporaryLocalStorage:
    def __init__(self, storage_dir="temp_storage"):
        # 初始化临时存储
        
    def add_item(self, data_type: str, item_id: str, item_data: dict) -> bool:
        # 添加项目到临时存储
        
    def get_item(self, data_type: str, item_id: str) -> Optional[dict]:
        # 从临时存储获取项目
        
    def sync_to_database(self, db_session_func) -> bool:
        # 将临时存储的数据同步到数据库
```

### 3. 增强本地缓存 (`enhanced_local_cache.py`)

#### 功能特性
- **双重存储**: 同时支持内存缓存和临时文件存储
- **智能同步**: 自动选择最优的同步策略
- **故障回退**: 数据库不可用时自动回退到本地存储
- **数据一致性**: 确保缓存与数据库数据的一致性

#### 主要类和方法

```python
class EnhancedLocalCache:
    def load_from_db_with_fallback(self) -> bool:
        # 从数据库加载数据，失败时使用临时存储
        
    def sync_to_db_with_fallback(self) -> bool:
        # 同步数据到数据库，失败时保存到临时存储
        
    def is_db_available(self) -> bool:
        # 检查数据库是否可用
```

### 4. 健康检查端点 (`routers/health.py`)

#### 功能特性
- **系统状态监控**: 实时监控各组件状态
- **详细诊断信息**: 提供详细的系统诊断数据
- **强制操作接口**: 支持强制同步和重连操作

#### 主要端点

```
GET  /health/           # 整体健康检查
GET  /health/database   # 数据库连接检查  
GET  /health/cache      # 本地缓存状态检查
POST /health/sync       # 强制数据同步
POST /health/reconnect  # 强制数据库重连
```

## 工作流程

### 1. 应用启动流程

```
启动应用
    ↓
初始化数据库连接管理器
    ↓
尝试连接数据库
    ↓
成功？→ 加载数据到本地缓存
    ↓ 失败
使用临时存储中的数据
    ↓
启动定时同步线程
    ↓
应用就绪
```

### 2. 数据库操作流程

```
数据库操作请求
    ↓
检查数据库连接
    ↓
可用？→ 执行数据库操作
    ↓ 不可用
尝试重连数据库
    ↓
成功？→ 执行数据库操作
    ↓ 失败
保存到临时存储
    ↓
返回操作结果
```

### 3. 数据同步流程

```
定时同步触发
    ↓
检查数据库连接
    ↓
可用？→ 同步本地缓存到数据库
    ↓ 不可用
保存到临时存储
    ↓
清理已同步数据
```

## 配置说明

### 环境变量

```bash
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# 连接参数（可选）
DB_CONNECTION_TIMEOUT=10
DB_RETRY_ATTEMPTS=3
DB_RETRY_DELAY=2
```

### 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 使用示例

### 1. 基本使用

```python
from enhanced_local_cache import enhanced_local_cache
from database_connection import db_manager

# 检查数据库连接
if db_manager.is_connection_available():
    print("数据库连接正常")
else:
    print("数据库连接不可用")

# 使用本地缓存
data = enhanced_local_cache.get_item("users", "user_id")
```

### 2. 健康检查

```bash
# 检查系统整体状态
curl http://localhost:8000/health/

# 检查数据库连接
curl http://localhost:8000/health/database

# 强制数据同步
curl -X POST http://localhost:8000/health/sync

# 强制数据库重连
curl -X POST http://localhost:8000/health/reconnect
```

### 3. 测试重连机制

```bash
# 运行测试脚本
python test_reconnection_mechanisms.py
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否运行
   - 验证数据库配置参数
   - 检查网络连接
   - 查看应用日志获取详细错误信息

2. **临时存储无法写入**
   - 检查磁盘空间
   - 验证文件权限
   - 确保存储目录存在

3. **同步失败**
   - 检查数据库连接状态
   - 验证数据格式
   - 查看同步日志

### 监控指标

- 数据库连接成功率
- 重连尝试次数
- 临时存储使用率
- 数据同步成功率
- 响应时间

### 日志分析

```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
grep ERROR app.log

# 查看数据库连接相关日志
grep "数据库连接" app.log
```

## 最佳实践

1. **定期测试重连机制**: 定期运行测试脚本，确保重连功能正常
2. **监控健康状态**: 使用健康检查端点监控系统状态
3. **配置合理的超时时间**: 根据网络环境调整连接超时参数
4. **备份临时存储**: 定期备份临时存储数据，防止数据丢失
5. **日志监控**: 建立日志监控和告警机制

## 性能优化

1. **连接池优化**: 根据并发量调整连接池大小
2. **同步频率**: 根据数据变化频率调整同步间隔
3. **临时存储清理**: 定期清理过期的临时数据
4. **内存管理**: 监控内存使用，避免缓存数据过多

## 安全考虑

1. **数据加密**: 敏感数据在临时存储中应该加密
2. **访问控制**: 限制健康检查端点的访问权限
3. **日志脱敏**: 避免在日志中记录敏感信息
4. **网络安全**: 确保数据库连接使用SSL/TLS

## 扩展功能

1. **多数据库支持**: 支持多个数据库的连接管理
2. **分布式缓存**: 集成Redis等分布式缓存系统
3. **数据压缩**: 对临时存储数据进行压缩
4. **增量同步**: 实现增量数据同步机制
5. **数据恢复**: 提供更完善的数据恢复工具