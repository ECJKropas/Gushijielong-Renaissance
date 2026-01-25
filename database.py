import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, 
    DateTime, Text, Float, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库配置
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

# 创建MySQL数据库引擎
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
# 尝试使用NullPool，避免连接池管理的查询开销
from sqlalchemy.pool import NullPool
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 关闭SQL日志输出，减少查询次数
    poolclass=NullPool,  # 使用NullPool，每次请求创建新连接，避免连接池查询
    connect_args={
        'charset': 'utf8mb4',
        'connect_timeout': 10,
        'read_timeout': 30,
        'write_timeout': 30,
        'ssl_ca': None,  # 使用系统CA证书启用SSL连接
    }  # 连接参数优化
)
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 创建基础模型
Base = declarative_base()
# 用户模型


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    registered_at = Column(DateTime, default=datetime.now)
    active_count = Column(Integer, default=0, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    credit = Column(Float, default=100.0, nullable=False)
    # 关系
    stories = relationship("StoryDB", back_populates="author")
    chapters = relationship("StoryChapterDB", back_populates="author")
    chapter_comments = relationship("ChapterCommentDB", back_populates="author")
    discussions = relationship("DiscussionDB", back_populates="author")
    discussion_comments = relationship("DiscussionCommentDB", back_populates="author")
# 故事模型


class StoryDB(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tags = Column(String(200), default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    # 关系
    author = relationship("UserDB", back_populates="stories")
    chapters = relationship("StoryChapterDB", back_populates="story")
# 章节模型


class StoryChapterDB(Base):
    __tablename__ = "story_chapters"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    # 关系
    story = relationship("StoryDB", back_populates="chapters")
    author = relationship("UserDB", back_populates="chapters")
    comments = relationship("ChapterCommentDB", back_populates="chapter")
# 章节评论模型


class ChapterCommentDB(Base):
    __tablename__ = "chapter_comments"
    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("story_chapters.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    # 关系
    chapter = relationship("StoryChapterDB", back_populates="comments")
    author = relationship("UserDB", back_populates="chapter_comments")
# 讨论主题模型


class DiscussionDB(Base):
    __tablename__ = "discussions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    # 关系
    author = relationship("UserDB", back_populates="discussions")
    comments = relationship("DiscussionCommentDB", back_populates="discussion")
# 讨论评论模型


class DiscussionCommentDB(Base):
    __tablename__ = "discussion_comments"
    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    # 关系
    discussion = relationship("DiscussionDB", back_populates="comments")
    author = relationship("UserDB", back_populates="discussion_comments")
# 数据库操作函数



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")



def migrate_data_from_memory(data_store):
    """从内存数据迁移到数据库"""
    db = SessionLocal()
    try:
        # 迁移用户数据
        for user_data in data_store.get("users", []):
            user = UserDB(
                id=user_data.id,
                username=user_data.username,
                email=user_data.email,
                password_hash=user_data.password_hash,
                role=user_data.role,
                registered_at=user_data.registered_at,
                active_count=user_data.active_count,
                points=user_data.points,
                credit=user_data.credit
            )
            db.add(user)
        # 迁移故事数据
        for story_data in data_store.get("stories", []):
            story = StoryDB(
                id=story_data.id,
                title=story_data.title,
                content=story_data.content,
                author_id=story_data.author_id,
                tags="",
                created_at=story_data.created_at,
                updated_at=story_data.updated_at
            )
            db.add(story)
        # 迁移章节数据
        for chapter_data in data_store.get("chapters", []):
            chapter = StoryChapterDB(
                id=chapter_data.id,
                story_id=chapter_data.story_id,
                content=chapter_data.content,
                author_id=chapter_data.author_id,
                author_name=chapter_data.author.username,
                created_at=chapter_data.created_at
            )
            db.add(chapter)
        # 迁移章节评论数据
        for comment_data in data_store.get("chapter_comments", []):
            comment = ChapterCommentDB(
                id=comment_data.id,
                chapter_id=comment_data.chapter_id,
                content=comment_data.content,
                author_id=comment_data.author_id,
                author_name=comment_data.author.username,
                created_at=comment_data.created_at
            )
            db.add(comment)
        # 迁移讨论数据
        for discussion_data in data_store.get("discussions", []):
            discussion = DiscussionDB(
                id=discussion_data.id,
                title=discussion_data.title,
                content=discussion_data.content,
                author_id=discussion_data.author_id,
                author_name=discussion_data.author.username,
                created_at=discussion_data.created_at
            )
            db.add(discussion)
        # 迁移讨论评论数据
        for comment_data in data_store.get("discussion_comments", []):
            comment = DiscussionCommentDB(
                id=comment_data.id,
                discussion_id=comment_data.discussion_id,
                content=comment_data.content,
                author_id=comment_data.author_id,
                author_name=comment_data.author.username,
                created_at=comment_data.created_at
            )
            db.add(comment)
        db.commit()
        print("数据迁移完成")
        return True
    except Exception as e:
        db.rollback()
        print(f"数据迁移失败: {e}")
        return False
    finally:
        db.close()
