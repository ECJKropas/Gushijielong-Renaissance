import os
import json
import pickle
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class TemporaryLocalStorage:
    """临时本地存储，当数据库不可用时使用"""
    
    def __init__(self, storage_dir: str = "temp_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 内存缓存
        self.data_cache = {
            "users": {},
            "stories": {},
            "story_chapters": {},
            "chapter_comments": {},
            "discussions": {},
            "discussion_comments": {}
        }
        
        # 修改跟踪
        self.modified_items = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set()
        }
        
        # 删除跟踪
        self.deleted_items = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set()
        }
        
        self.lock = threading.RLock()
        self.last_persist_time = datetime.now()
        self.persist_interval = timedelta(minutes=5)  # 每5分钟持久化一次
        
        # 加载已持久化的数据
        self._load_persisted_data()
        
    def _get_storage_file(self, data_type: str) -> Path:
        """获取存储文件路径"""
        return self.storage_dir / f"{data_type}.json"
        
    def _load_persisted_data(self):
        """从文件加载持久化数据"""
        with self.lock:
            for data_type in self.data_cache.keys():
                storage_file = self._get_storage_file(data_type)
                if storage_file.exists():
                    try:
                        with open(storage_file, 'r', encoding='utf-8') as f:
                            self.data_cache[data_type] = json.load(f)
                        logger.info(f"从文件加载 {data_type} 数据成功")
                    except Exception as e:
                        logger.error(f"加载 {data_type} 数据失败: {str(e)}")
                        
    def _persist_data(self, data_type: str):
        """持久化特定类型的数据到文件"""
        with self.lock:
            try:
                storage_file = self._get_storage_file(data_type)
                with open(storage_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data_cache[data_type], f, ensure_ascii=False, indent=2)
                logger.debug(f"持久化 {data_type} 数据成功")
            except Exception as e:
                logger.error(f"持久化 {data_type} 数据失败: {str(e)}")
                
    def _should_persist(self) -> bool:
        """检查是否应该进行持久化"""
        return datetime.now() - self.last_persist_time > self.persist_interval
        
    def auto_persist(self):
        """自动持久化修改过的数据"""
        if not self._should_persist():
            return
            
        with self.lock:
            for data_type, modified_set in self.modified_items.items():
                if modified_set:
                    self._persist_data(data_type)
                    
            self.last_persist_time = datetime.now()
            
    def add_item(self, data_type: str, item_id: str, item_data: Dict[str, Any]):
        """添加项目到临时存储"""
        with self.lock:
            if data_type not in self.data_cache:
                logger.error(f"未知的数据类型: {data_type}")
                return False
                
            try:
                # 添加时间戳
                item_data['_temp_storage_time'] = datetime.now().isoformat()
                item_data['_temp_id'] = item_id
                
                self.data_cache[data_type][item_id] = item_data
                self.modified_items[data_type].add(item_id)
                
                logger.info(f"添加 {data_type} 项目 {item_id} 到临时存储")
                return True
                
            except Exception as e:
                logger.error(f"添加项目失败: {str(e)}")
                return False
                
    def get_item(self, data_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """从临时存储获取项目"""
        with self.lock:
            return self.data_cache[data_type].get(item_id)
            
    def get_all_items(self, data_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的所有项目"""
        with self.lock:
            return list(self.data_cache[data_type].values())
            
    def update_item(self, data_type: str, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新临时存储中的项目"""
        with self.lock:
            if item_id not in self.data_cache[data_type]:
                return False
                
            try:
                # 获取现有数据
                existing_data = self.data_cache[data_type][item_id]
                
                # 保留临时存储的元数据
                temp_meta = {k: v for k, v in existing_data.items() if k.startswith('_temp_')}
                
                # 更新数据
                existing_data.update(updates)
                existing_data.update(temp_meta)
                existing_data['_temp_update_time'] = datetime.now().isoformat()
                
                self.modified_items[data_type].add(item_id)
                
                logger.info(f"更新 {data_type} 项目 {item_id}")
                return True
                
            except Exception as e:
                logger.error(f"更新项目失败: {str(e)}")
                return False
                
    def delete_item(self, data_type: str, item_id: str) -> bool:
        """从临时存储删除项目"""
        with self.lock:
            if item_id in self.data_cache[data_type]:
                del self.data_cache[data_type][item_id]
                self.deleted_items[data_type].add(item_id)
                self.modified_items[data_type].discard(item_id)
                
                logger.info(f"删除 {data_type} 项目 {item_id}")
                return True
            return False
            
    def get_modified_items(self, data_type: str) -> List[Dict[str, Any]]:
        """获取指定类型的修改过的项目"""
        with self.lock:
            modified_ids = self.modified_items[data_type]
            return [
                self.data_cache[data_type][item_id] 
                for item_id in modified_ids 
                if item_id in self.data_cache[data_type]
            ]
            
    def get_deleted_item_ids(self, data_type: str) -> Set[str]:
        """获取指定类型的已删除项目ID"""
        with self.lock:
            return self.deleted_items[data_type].copy()
            
    def clear_modified_flags(self, data_type: str):
        """清除指定类型的修改标记"""
        with self.lock:
            self.modified_items[data_type].clear()
            self.deleted_items[data_type].clear()
            
    def sync_to_database(self, db_session_func) -> bool:
        """将临时存储的数据同步到数据库"""
        try:
            success_count = 0
            total_count = 0
            
            for data_type in self.data_cache.keys():
                # 同步修改过的项目
                modified_items = self.get_modified_items(data_type)
                for item in modified_items:
                    total_count += 1
                    try:
                        # 这里应该调用具体的数据库同步逻辑
                        # 需要传入 db_session_func 来处理具体的数据库操作
                        if self._sync_item_to_db(data_type, item, db_session_func):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"同步 {data_type} 项目 {item.get('_temp_id')} 失败: {str(e)}")
                        
                # 同步删除操作
                deleted_ids = self.get_deleted_item_ids(data_type)
                for item_id in deleted_ids:
                    total_count += 1
                    try:
                        if self._sync_delete_to_db(data_type, item_id, db_session_func):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"同步删除 {data_type} 项目 {item_id} 失败: {str(e)}")
                        
            logger.info(f"临时存储同步完成: 成功 {success_count}/{total_count}")
            
            # 清除修改标记
            if success_count == total_count:
                for data_type in self.data_cache.keys():
                    self.clear_modified_flags(data_type)
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"临时存储同步失败: {str(e)}")
            return False
            
    def _sync_item_to_db(self, data_type: str, item: Dict[str, Any], db_session_func) -> bool:
        """同步单个项目到数据库"""
        # 这个方法需要具体实现，根据数据类型调用相应的数据库操作
        # 这里只是一个框架
        try:
            # 清理临时存储的元数据
            clean_item = {k: v for k, v in item.items() if not k.startswith('_temp_')}
            
            # 调用数据库会话函数进行实际的同步操作
            # 这里需要根据具体的数据类型和数据库模型来实现
            return db_session_func(data_type, clean_item)
            
        except Exception as e:
            logger.error(f"同步项目到数据库失败: {str(e)}")
            return False
            
    def _sync_delete_to_db(self, data_type: str, item_id: str, db_session_func) -> bool:
        """同步删除操作到数据库"""
        try:
            # 调用数据库会话函数进行实际的删除操作
            return db_session_func(f"delete_{data_type}", item_id)
            
        except Exception as e:
            logger.error(f"同步删除操作到数据库失败: {str(e)}")
            return False
            
    def cleanup_old_data(self, days_to_keep: int = 7):
        """清理旧的临时数据"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with self.lock:
            for data_type in self.data_cache.keys():
                items_to_remove = []
                
                for item_id, item_data in self.data_cache[data_type].items():
                    storage_time = item_data.get('_temp_storage_time')
                    if storage_time:
                        try:
                            storage_dt = datetime.fromisoformat(storage_time)
                            if storage_dt < cutoff_date:
                                items_to_remove.append(item_id)
                        except Exception as e:
                            logger.error(f"解析时间失败: {str(e)}")
                            
                # 移除旧数据
                for item_id in items_to_remove:
                    del self.data_cache[data_type][item_id]
                    
                if items_to_remove:
                    logger.info(f"清理 {data_type} 的旧数据: {len(items_to_remove)} 项")
                    self._persist_data(data_type)

# 创建全局临时存储实例
temp_storage = TemporaryLocalStorage()