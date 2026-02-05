import os
import json
import threading
from datetime import datetime, timedelta
from database import SessionLocal
from sqlalchemy.orm import Session

# 本地缓存类
class LocalCache:
    def __init__(self):
        self.data = {
            "users": {},
            "stories": {},
            "story_chapters": {},
            "chapter_comments": {},
            "discussions": {},
            "discussion_comments": {}
        }
        self.modified = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set()
        }
        self.deleted = {
            "users": set(),
            "stories": set(),
            "story_chapters": set(),
            "chapter_comments": set(),
            "discussions": set(),
            "discussion_comments": set()
        }
        # IP限流缓存
        self.ip_register_times = {}
        self.lock = threading.Lock()
        self.last_sync_time = datetime.now()
    
    def check_ip_rate_limit(self, ip_address):
        """检查IP地址的注册频率限制
        返回True表示通过限制，False表示频率过高
        """
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
    
    def _get_class_by_table(self, table_name):
        """根据表名获取对应的数据库模型类"""
        from database import (
            UserDB,
            StoryDB,
            StoryChapterDB,
            ChapterCommentDB,
            DiscussionDB,
            DiscussionCommentDB
        )
        
        table_class_map = {
            "users": UserDB,
            "stories": StoryDB,
            "story_chapters": StoryChapterDB,
            "chapter_comments": ChapterCommentDB,
            "discussions": DiscussionDB,
            "discussion_comments": DiscussionCommentDB
        }
        return table_class_map.get(table_name)
    
    def load_from_db(self, db: Session):
        """从数据库加载初始数据到本地缓存"""
        from database import (
            UserDB,
            StoryDB,
            StoryChapterDB,
            ChapterCommentDB,
            DiscussionDB,
            DiscussionCommentDB
        )
        
        # 加载所有数据
        with self.lock:
            # 加载用户
            users = db.query(UserDB).all()
            for user in users:
                self.data["users"][user.id] = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "password_hash": user.password_hash,
                    "role": user.role,
                    "registered_at": user.registered_at,
                    "active_count": user.active_count,
                    "points": user.points,
                    "credit": user.credit
                }
            
            # 加载故事
            stories = db.query(StoryDB).all()
            for story in stories:
                self.data["stories"][story.id] = {
                    "id": story.id,
                    "title": story.title,
                    "content": story.content,
                    "author_id": story.author_id,
                    "tags": story.tags,
                    "created_at": story.created_at,
                    "updated_at": story.updated_at
                }
            
            # 加载章节
            chapters = db.query(StoryChapterDB).all()
            for chapter in chapters:
                self.data["story_chapters"][chapter.id] = {
                    "id": chapter.id,
                    "story_id": chapter.story_id,
                    "content": chapter.content,
                    "author_id": chapter.author_id,
                    "author_name": chapter.author_name,
                    "created_at": chapter.created_at
                }
            
            # 加载章节评论
            chapter_comments = db.query(ChapterCommentDB).all()
            for comment in chapter_comments:
                self.data["chapter_comments"][comment.id] = {
                    "id": comment.id,
                    "chapter_id": comment.chapter_id,
                    "content": comment.content,
                    "author_id": comment.author_id,
                    "author_name": comment.author_name,
                    "created_at": comment.created_at
                }
            
            # 加载讨论
            discussions = db.query(DiscussionDB).all()
            for discussion in discussions:
                self.data["discussions"][discussion.id] = {
                    "id": discussion.id,
                    "title": discussion.title,
                    "content": discussion.content,
                    "author_id": discussion.author_id,
                    "author_name": discussion.author_name,
                    "created_at": discussion.created_at
                }
            
            # 加载讨论评论
            discussion_comments = db.query(DiscussionCommentDB).all()
            for comment in discussion_comments:
                self.data["discussion_comments"][comment.id] = {
                    "id": comment.id,
                    "discussion_id": comment.discussion_id,
                    "content": comment.content,
                    "author_id": comment.author_id,
                    "author_name": comment.author_name,
                    "created_at": comment.created_at
                }
            
            self.last_sync_time = datetime.now()
            print("数据已从数据库加载到本地缓存")
    
    def get(self, table_name, item_id):
        """从本地缓存获取数据"""
        with self.lock:
            return self.data.get(table_name, {}).get(item_id)
    
    def get_all(self, table_name):
        """从本地缓存获取所有数据"""
        with self.lock:
            return list(self.data.get(table_name, {}).values())
    
    def add(self, table_name, item):
        """添加数据到本地缓存"""
        with self.lock:
            # 支持字典和对象两种类型
            if isinstance(item, dict):
                item_id = item.get("id")
            else:
                item_id = getattr(item, "id", None)
            if item_id:
                self.data[table_name][item_id] = item
                self.modified[table_name].add(item_id)
                # 如果之前标记为删除，取消删除标记
                if item_id in self.deleted[table_name]:
                    self.deleted[table_name].remove(item_id)
                return item
            return None
    
    def update(self, table_name, item):
        """更新本地缓存中的数据"""
        with self.lock:
            # 支持字典和对象两种类型
            if isinstance(item, dict):
                item_id = item.get("id")
            else:
                item_id = getattr(item, "id", None)
            if item_id and item_id in self.data[table_name]:
                self.data[table_name][item_id] = item
                self.modified[table_name].add(item_id)
                # 如果之前标记为删除，取消删除标记
                if item_id in self.deleted[table_name]:
                    self.deleted[table_name].remove(item_id)
                return item
            return None
    
    def delete(self, table_name, item_id):
        """从本地缓存删除数据"""
        with self.lock:
            if item_id in self.data[table_name]:
                del self.data[table_name][item_id]
                self.deleted[table_name].add(item_id)
                # 如果之前标记为修改，取消修改标记
                if item_id in self.modified[table_name]:
                    self.modified[table_name].remove(item_id)
                return True
            return False
    
    def sync_to_db(self):
        """将本地修改同步到数据库"""
        db = SessionLocal()
        try:
            with self.lock:
                # 同步每个表的数据
                for table_name in self.data.keys():
                    self._sync_table(db, table_name)
                
                # 提交事务，这是关键！
                db.commit()
                
                self.last_sync_time = datetime.now()
                print(f"数据已同步到数据库，时间: {self.last_sync_time}")
                return True
        except Exception as e:
            db.rollback()
            print(f"数据同步失败: {e}")
            return False
        finally:
            db.close()
    
    def sync_to_db(self):
        """将本地修改同步到数据库"""
        # 检查数据库是否可用
        from database import is_db_available
        if not is_db_available():
            print("数据库不可用，跳过同步操作")
            return False
        
        from database import SessionLocal
        if not SessionLocal:
            print("数据库引擎未初始化，跳过同步操作")
            return False
        
        db = SessionLocal()
        try:
            with self.lock:
                # 同步删除操作，按照正确的顺序处理外键约束
                # 1. 先删除所有评论
                for table_name in ["chapter_comments", "discussion_comments"]:
                    self._sync_deletes(db, table_name)
                
                # 2. 再删除所有章节
                self._sync_deletes(db, "story_chapters")
                
                # 3. 最后删除所有主表数据
                for table_name in ["stories", "discussions"]:
                    self._sync_deletes(db, table_name)
                
                # 4. 删除用户数据
                self._sync_deletes(db, "users")
                
                # 同步修改操作
                for table_name in self.data.keys():
                    self._sync_modifies(db, table_name)
                
                # 提交事务，这是关键！
                db.commit()
                
                self.last_sync_time = datetime.now()
                print(f"数据已同步到数据库，时间: {self.last_sync_time}")
                return True
        except Exception as e:
            db.rollback()
            print(f"数据同步失败: {e}")
            return False
        finally:
            db.close()
    
    def _sync_deletes(self, db: Session, table_name):
        """同步删除操作"""
        model_class = self._get_class_by_table(table_name)
        if not model_class:
            return
        
        # 处理删除的数据
        for item_id in self.deleted[table_name]:
            try:
                # 从数据库删除
                db.query(model_class).filter(model_class.id == item_id).delete()
            except Exception as e:
                print(f"删除 {table_name} {item_id} 失败: {e}")
        # 清空删除标记
        self.deleted[table_name].clear()
    
    def _sync_modifies(self, db: Session, table_name):
        """同步修改操作"""
        model_class = self._get_class_by_table(table_name)
        if not model_class:
            return
        
        # 处理修改的数据
        for item_id in self.modified[table_name]:
            try:
                item = self.data[table_name].get(item_id)
                if item:
                    # 检查数据库中是否存在
                    db_item = db.query(model_class).filter(model_class.id == item_id).first()
                    if db_item:
                        # 更新现有数据
                        for column in model_class.__table__.columns:
                            if column.name != "id":
                                setattr(db_item, column.name, item.get(column.name))
                        db.merge(db_item)
                    else:
                        # 添加新数据
                        # 创建模型实例
                        new_item = model_class()
                        for column in model_class.__table__.columns:
                            setattr(new_item, column.name, item.get(column.name))
                        db.add(new_item)
            except Exception as e:
                print(f"同步 {table_name} {item_id} 失败: {e}")
        # 清空修改标记
        self.modified[table_name].clear()

# 创建全局缓存实例
local_cache = LocalCache()
