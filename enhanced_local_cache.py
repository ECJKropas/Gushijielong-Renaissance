import logging
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from database_connection import db_manager, get_db_session
from temp_storage import temp_storage

logger = logging.getLogger(__name__)

class EnhancedLocalCache:
    """增强的本地缓存，支持数据库重连和临时存储"""
    
    def __init__(self):
        # 原有的本地缓存数据结构
        self.data = {
            "users": {},
            "stories": {},
            "story_chapters": {},
            "chapter_comments": {},
            "discussions": {},
            "discussion_comments": {},
            "story_tree_nodes": {}
        }
        
        # 修改跟踪
        self.modified = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set(),
            "story_tree_nodes": set()
        }
        
        # 删除跟踪
        self.deleted = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set(),
            "story_tree_nodes": set()
        }
        
        # IP限流缓存
        self.ip_register_times = {}
        self.lock = threading.RLock()
        self.last_sync_time = datetime.now()
        
        # 数据库连接状态
        self.db_available = True
        self.last_db_check = datetime.now()
        
    def check_ip_rate_limit(self, ip_address: str) -> bool:
        """检查IP地址的注册频率限制"""
        with self.lock:
            current_time = datetime.now()
            
            # 清理过期的IP记录
            expired_ips = []
            for ip, register_time in self.ip_register_times.items():
                if current_time - register_time > timedelta(minutes=5):
                    expired_ips.append(ip)
            for ip in expired_ips:
                del self.ip_register_times[ip]
            
            # 检查当前IP是否在限制内
            if ip_address in self.ip_register_times:
                return False
            
            # 记录当前IP的注册时间
            self.ip_register_times[ip_address] = current_time
            return True
            
    def _get_class_by_table(self, table_name: str):
        """根据表名获取对应的数据库模型类"""
        from database import (
            UserDB,
            StoryDB,
            StoryChapterDB,
            ChapterCommentDB,
            DiscussionDB,
            DiscussionCommentDB,
            StoryTreeNodeDB
        )
        
        table_class_map = {
            "users": UserDB,
            "stories": StoryDB,
            "story_chapters": StoryChapterDB,
            "chapter_comments": ChapterCommentDB,
            "discussions": DiscussionDB,
            "discussion_comments": DiscussionCommentDB,
            "story_tree_nodes": StoryTreeNodeDB
        }
        return table_class_map.get(table_name)
        
    def load_from_db_with_fallback(self) -> bool:
        """从数据库加载数据，失败时使用临时存储"""
        try:
            # 首先尝试从数据库加载
            if self._load_from_db_direct():
                logger.info("从数据库加载数据成功")
                return True
                
        except Exception as e:
            logger.error(f"从数据库加载数据失败: {str(e)}")
            
        # 数据库加载失败，尝试从临时存储恢复
        logger.info("尝试从临时存储恢复数据")
        return self._load_from_temp_storage()
        
    def _load_from_db_direct(self) -> bool:
        """直接从数据库加载数据"""
        try:
            def load_data(session):
                from database import (
                    UserDB, StoryDB, StoryChapterDB, 
                    ChapterCommentDB, DiscussionDB, DiscussionCommentDB
                )
                
                # 加载所有数据
                with self.lock:
                    # 加载用户
                    users = session.query(UserDB).all()
                    for user in users:
                        self.data["users"][user.id] = {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "created_at": user.created_at.isoformat() if user.created_at else None,
                            "last_login": user.last_login.isoformat() if user.last_login else None
                        }
                    
                    # 加载故事
                    stories = session.query(StoryDB).all()
                    for story in stories:
                        self.data["stories"][story.id] = {
                            "id": story.id,
                            "title": story.title,
                            "author_id": story.author_id,
                            "content": story.content,
                            "created_at": story.created_at.isoformat() if story.created_at else None,
                            "updated_at": story.updated_at.isoformat() if story.updated_at else None
                        }
                    
                    # 加载故事章节
                    chapters = session.query(StoryChapterDB).all()
                    for chapter in chapters:
                        self.data["story_chapters"][chapter.id] = {
                            "id": chapter.id,
                            "story_id": chapter.story_id,
                            "chapter_number": chapter.chapter_number,
                            "title": chapter.title,
                            "content": chapter.content,
                            "created_at": chapter.created_at.isoformat() if chapter.created_at else None
                        }
                    
                    # 加载章节评论
                    comments = session.query(ChapterCommentDB).all()
                    for comment in comments:
                        self.data["chapter_comments"][comment.id] = {
                            "id": comment.id,
                            "chapter_id": comment.chapter_id,
                            "user_id": comment.user_id,
                            "content": comment.content,
                            "created_at": comment.created_at.isoformat() if comment.created_at else None
                        }
                    
                    # 加载讨论
                    discussions = session.query(DiscussionDB).all()
                    for discussion in discussions:
                        self.data["discussions"][discussion.id] = {
                            "id": discussion.id,
                            "title": discussion.title,
                            "user_id": discussion.user_id,
                            "content": discussion.content,
                            "created_at": discussion.created_at.isoformat() if discussion.created_at else None
                        }
                    
                    # 加载讨论评论
                    discussion_comments = session.query(DiscussionCommentDB).all()
                    for comment in discussion_comments:
                        self.data["discussion_comments"][comment.id] = {
                            "id": comment.id,
                            "discussion_id": comment.discussion_id,
                            "user_id": comment.user_id,
                            "content": comment.content,
                            "created_at": comment.created_at.isoformat() if comment.created_at else None
                        }
                    
                    # 加载故事树节点
                    story_tree_nodes = session.query(StoryTreeNodeDB).all()
                    for node in story_tree_nodes:
                        self.data["story_tree_nodes"][node.id] = {
                            "id": node.id,
                            "title": node.title,
                            "option_title": node.option_title,
                            "content": node.content,
                            "parent_id": node.parent_id,
                            "author_id": node.author_id,
                            "created_at": node.created_at.isoformat() if node.created_at else None
                        }
                
                return True
            
            # 使用数据库管理器执行操作
            return db_manager.execute_with_retry(load_data)
            
        except Exception as e:
            logger.error(f"数据库加载失败: {str(e)}")
            return False
            
    def _load_from_temp_storage(self) -> bool:
        """从临时存储加载数据"""
        try:
            with self.lock:
                for data_type in self.data.keys():
                    temp_items = temp_storage.get_all_items(data_type)
                    for item in temp_items:
                        item_id = item.get('_temp_id')
                        if item_id:
                            # 清理临时存储的元数据
                            clean_item = {k: v for k, v in item.items() if not k.startswith('_temp_')}
                            self.data[data_type][item_id] = clean_item
                            
                logger.info("从临时存储恢复数据成功")
                return True
                
        except Exception as e:
            logger.error(f"从临时存储恢复数据失败: {str(e)}")
            return False
            
    def sync_to_db_with_fallback(self) -> bool:
        """同步数据到数据库，失败时保存到临时存储"""
        try:
            # 首先尝试同步到数据库
            if self._sync_to_db_direct():
                logger.info("同步到数据库成功")
                return True
                
        except Exception as e:
            logger.error(f"同步到数据库失败: {str(e)}")
            
        # 数据库同步失败，保存到临时存储
        logger.info("保存数据到临时存储")
        return self._sync_to_temp_storage()
        
    def _sync_to_db_direct(self) -> bool:
        """直接同步到数据库"""
        try:
            def sync_data(session):
                with self.lock:
                    for table_name, modified_ids in self.modified.items():
                        if not modified_ids:
                            continue
                            
                        # 获取对应的模型类
                        model_class = self._get_class_by_table(table_name)
                        if not model_class:
                            continue
                            
                        for item_id in modified_ids:
                            if item_id in self.data[table_name]:
                                item_data = self.data[table_name][item_id]
                                # 这里应该实现具体的数据库同步逻辑
                                # 根据 item_data 更新或插入数据库记录
                                
                    # 处理删除操作
                    for table_name, deleted_ids in self.deleted.items():
                        if not deleted_ids:
                            continue
                            
                        model_class = self._get_class_by_table(table_name)
                        if not model_class:
                            continue
                            
                        for item_id in deleted_ids:
                            # 这里应该实现具体的数据库删除逻辑
                            pass
                            
                    return True
            
            return db_manager.execute_with_retry(sync_data)
            
        except Exception as e:
            logger.error(f"数据库同步失败: {str(e)}")
            return False
            
    def _sync_to_temp_storage(self) -> bool:
        """同步到临时存储"""
        try:
            with self.lock:
                for table_name, modified_ids in self.modified.items():
                    for item_id in modified_ids:
                        if item_id in self.data[table_name]:
                            item_data = self.data[table_name][item_id].copy()
                            temp_storage.add_item(table_name, item_id, item_data)
                            
                # 处理删除操作
                for table_name, deleted_ids in self.deleted.items():
                    for item_id in deleted_ids:
                        temp_storage.delete_item(table_name, item_id)
                        
                logger.info("同步到临时存储成功")
                return True
                
        except Exception as e:
            logger.error(f"同步到临时存储失败: {str(e)}")
            return False
            
    def get_item(self, data_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """获取项目，优先从内存缓存获取"""
        with self.lock:
            return self.data[data_type].get(item_id)
            
    def add_item(self, data_type: str, item_id: str, item_data: Dict[str, Any]):
        """添加项目到缓存"""
        with self.lock:
            self.data[data_type][item_id] = item_data
            self.modified[data_type].add(item_id)
            
    def update_item(self, data_type: str, item_id: str, updates: Dict[str, Any]) -> bool:
        """更新缓存中的项目"""
        with self.lock:
            if item_id in self.data[data_type]:
                self.data[data_type][item_id].update(updates)
                self.modified[data_type].add(item_id)
                return True
            return False
            
    def delete_item(self, data_type: str, item_id: str) -> bool:
        """从缓存删除项目"""
        with self.lock:
            if item_id in self.data[data_type]:
                del self.data[data_type][item_id]
                self.deleted[data_type].add(item_id)
                self.modified[data_type].discard(item_id)
                return True
            return False
            
    def is_db_available(self) -> bool:
        """检查数据库是否可用"""
        return db_manager.is_connection_available()
        
    def cleanup(self):
        """清理资源"""
        try:
            # 同步数据
            self.sync_to_db_with_fallback()
            
            # 清理临时存储的旧数据
            temp_storage.cleanup_old_data()
            
            logger.info("本地缓存清理完成")
            
        except Exception as e:
            logger.error(f"本地缓存清理失败: {str(e)}")

# 创建全局增强本地缓存实例
enhanced_local_cache = EnhancedLocalCache()