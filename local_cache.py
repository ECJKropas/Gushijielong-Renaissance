import os
import json
import threading
from datetime import datetime
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
        self.lock = threading.Lock()
        self.last_sync_time = datetime.now()
    
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
                self.data["users"][user.id] = user
            
            # 加载故事
            stories = db.query(StoryDB).all()
            for story in stories:
                self.data["stories"][story.id] = story
            
            # 加载章节
            chapters = db.query(StoryChapterDB).all()
            for chapter in chapters:
                self.data["story_chapters"][chapter.id] = chapter
            
            # 加载章节评论
            chapter_comments = db.query(ChapterCommentDB).all()
            for comment in chapter_comments:
                self.data["chapter_comments"][comment.id] = comment
            
            # 加载讨论
            discussions = db.query(DiscussionDB).all()
            for discussion in discussions:
                self.data["discussions"][discussion.id] = discussion
            
            # 加载讨论评论
            discussion_comments = db.query(DiscussionCommentDB).all()
            for comment in discussion_comments:
                self.data["discussion_comments"][comment.id] = comment
            
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
    
    def _sync_table(self, db: Session, table_name):
        """同步单个表的数据"""
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
                                setattr(db_item, column.name, getattr(item, column.name))
                        db.merge(db_item)
                    else:
                        # 添加新数据
                        db.add(item)
            except Exception as e:
                print(f"同步 {table_name} {item_id} 失败: {e}")
        # 清空修改标记
        self.modified[table_name].clear()

# 创建全局缓存实例
local_cache = LocalCache()
