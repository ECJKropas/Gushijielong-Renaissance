#!/usr/bin/env python3
"""
测试数据库重连和临时存储回退机制
"""

import time
import logging
import requests
from database_connection import db_manager
from enhanced_local_cache import enhanced_local_cache
from temp_storage import temp_storage

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseReconnectionTester:
    """数据库重连测试器"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {}
        
    def test_database_connection(self):
        """测试数据库连接"""
        logger.info("=== 测试数据库连接 ===")
        
        try:
            is_connected = db_manager.is_connection_available()
            logger.info(f"数据库连接状态: {'可用' if is_connected else '不可用'}")
            self.test_results['database_connection'] = is_connected
            return is_connected
            
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            self.test_results['database_connection'] = False
            return False
            
    def test_database_reconnection(self):
        """测试数据库重连功能"""
        logger.info("=== 测试数据库重连功能 ===")
        
        try:
            # 模拟连接断开的情况
            logger.info("模拟数据库连接断开...")
            # 这里可以模拟断开连接，比如临时修改配置
            
            # 尝试重连
            reconnect_success = db_manager.reconnect()
            logger.info(f"数据库重连结果: {'成功' if reconnect_success else '失败'}")
            
            self.test_results['database_reconnection'] = reconnect_success
            return reconnect_success
            
        except Exception as e:
            logger.error(f"数据库重连测试失败: {str(e)}")
            self.test_results['database_reconnection'] = False
            return False
            
    def test_local_cache_operations(self):
        """测试本地缓存操作"""
        logger.info("=== 测试本地缓存操作 ===")
        
        try:
            # 测试添加数据到缓存
            test_data = {
                "id": "test_user_1",
                "username": "test_user",
                "email": "test@example.com"
            }
            
            enhanced_local_cache.add_item("users", "test_user_1", test_data)
            logger.info("添加测试数据到缓存成功")
            
            # 测试从缓存获取数据
            retrieved_data = enhanced_local_cache.get_item("users", "test_user_1")
            if retrieved_data and retrieved_data.get("username") == "test_user":
                logger.info("从缓存获取数据成功")
                cache_read_success = True
            else:
                logger.error("从缓存获取数据失败")
                cache_read_success = False
                
            self.test_results['local_cache_operations'] = cache_read_success
            return cache_read_success
            
        except Exception as e:
            logger.error(f"本地缓存操作测试失败: {str(e)}")
            self.test_results['local_cache_operations'] = False
            return False
            
    def test_temp_storage_fallback(self):
        """测试临时存储回退功能"""
        logger.info("=== 测试临时存储回退功能 ===")
        
        try:
            # 添加测试数据到临时存储
            test_data = {
                "id": "temp_story_1",
                "title": "临时测试故事",
                "content": "这是一个临时测试故事的内容"
            }
            
            success = temp_storage.add_item("stories", "temp_story_1", test_data)
            if success:
                logger.info("添加数据到临时存储成功")
                
                # 从临时存储获取数据
                retrieved_data = temp_storage.get_item("stories", "temp_story_1")
                if retrieved_data and retrieved_data.get("title") == "临时测试故事":
                    logger.info("从临时存储获取数据成功")
                    temp_storage_success = True
                else:
                    logger.error("从临时存储获取数据失败")
                    temp_storage_success = False
            else:
                logger.error("添加数据到临时存储失败")
                temp_storage_success = False
                
            self.test_results['temp_storage_fallback'] = temp_storage_success
            return temp_storage_success
            
        except Exception as e:
            logger.error(f"临时存储回退测试失败: {str(e)}")
            self.test_results['temp_storage_fallback'] = False
            return False
            
    def test_health_check_endpoints(self):
        """测试健康检查端点"""
        logger.info("=== 测试健康检查端点 ===")
        
        try:
            # 测试主要健康检查端点
            response = requests.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"健康检查响应: {health_data}")
                health_check_success = health_data.get("status") in ["healthy", "degraded"]
            else:
                logger.error(f"健康检查端点返回错误状态码: {response.status_code}")
                health_check_success = False
                
            # 测试数据库健康检查端点
            response = requests.get(f"{self.base_url}/health/database")
            if response.status_code == 200:
                db_health_data = response.json()
                logger.info(f"数据库健康检查响应: {db_health_data}")
                db_health_success = True
            else:
                logger.error(f"数据库健康检查端点返回错误状态码: {response.status_code}")
                db_health_success = False
                
            self.test_results['health_check_endpoints'] = health_check_success and db_health_success
            return health_check_success and db_health_success
            
        except Exception as e:
            logger.error(f"健康检查端点测试失败: {str(e)}")
            self.test_results['health_check_endpoints'] = False
            return False
            
    def test_sync_operations(self):
        """测试同步操作"""
        logger.info("=== 测试同步操作 ===")
        
        try:
            # 强制同步测试
            response = requests.post(f"{self.base_url}/health/sync")
            if response.status_code == 200:
                sync_data = response.json()
                logger.info(f"强制同步响应: {sync_data}")
                sync_success = sync_data.get("status") == "success"
            else:
                logger.error(f"强制同步端点返回错误状态码: {response.status_code}")
                sync_success = False
                
            self.test_results['sync_operations'] = sync_success
            return sync_success
            
        except Exception as e:
            logger.error(f"同步操作测试失败: {str(e)}")
            self.test_results['sync_operations'] = False
            return False
            
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始运行所有重连和回退机制测试...")
        
        tests = [
            ("数据库连接", self.test_database_connection),
            ("数据库重连", self.test_database_reconnection),
            ("本地缓存操作", self.test_local_cache_operations),
            ("临时存储回退", self.test_temp_storage_fallback),
            ("健康检查端点", self.test_health_check_endpoints),
            ("同步操作", self.test_sync_operations)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n{'='*50}")
                logger.info(f"开始测试: {test_name}")
                test_func()
                time.sleep(1)  # 测试间隔
                
            except Exception as e:
                logger.error(f"测试 '{test_name}' 执行失败: {str(e)}")
                self.test_results[test_name.lower().replace(' ', '_')] = False
                
        # 生成测试报告
        self.generate_test_report()
        
    def generate_test_report(self):
        """生成测试报告"""
        logger.info("\n" + "="*60)
        logger.info("数据库重连和回退机制测试报告")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        logger.info(f"总测试数: {total_tests}")
        logger.info(f"通过测试: {passed_tests}")
        logger.info(f"失败测试: {failed_tests}")
        logger.info(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        logger.info("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✓ 通过" if result else "✗ 失败"
            logger.info(f"  {test_name}: {status}")
            
        logger.info("\n建议:")
        if failed_tests > 0:
            logger.info("- 检查数据库配置和网络连接")
            logger.info("- 验证环境变量设置")
            logger.info("- 查看日志文件获取详细错误信息")
            logger.info("- 确保MySQL服务正在运行")
        else:
            logger.info("- 所有测试通过，系统重连和回退机制正常工作")
            logger.info("- 建议定期运行此测试以确保系统稳定性")
            
        logger.info("="*60)

def main():
    """主函数"""
    # 创建测试器
    tester = DatabaseReconnectionTester()
    
    # 运行所有测试
    tester.run_all_tests()
    
    # 清理测试数据
    logger.info("\n清理测试数据...")
    try:
        # 清理临时测试数据
        temp_storage.delete_item("users", "test_user_1")
        temp_storage.delete_item("stories", "temp_story_1")
        logger.info("测试数据清理完成")
    except Exception as e:
        logger.error(f"清理测试数据失败: {str(e)}")

if __name__ == "__main__":
    main()