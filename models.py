from datetime import datetime
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import get_user_by_id
# 获取当前登录用户ID


def get_current_user_id(request: Request):
    user_id = request.cookies.get("user_id")
    if user_id:
        try:
            return int(user_id)
        except (ValueError, TypeError):
            pass
    return None
# 获取当前登录用户对象


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request)
    if user_id:
        return get_user_by_id(db, user_id)
    return None


class User:


    def __init__(self, id: int, username: str, email: str, password_hash: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = "user"  # 默认普通用户
        self.registered_at = datetime.now()
        self.active_count = 0
        self.points = 0
        self.credit = 100.0  # 初始信用分


class Story:


    def __init__(self, id: int, title: str, content: str, author_id: int):
        self.id = id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class StoryChapter:


    def __init__(self, id: int, story_id: int, content: str, author: str, author_id: int):
        self.id = id
        self.story_id = story_id
        self.content = content
        self.author = author
        self.author_id = author_id
        self.created_at = datetime.now()


class ChapterComment:


    def __init__(self, id: int, chapter_id: int, content: str, author: str, author_id: int):
        self.id = id
        self.chapter_id = chapter_id
        self.content = content
        self.author = author
        self.author_id = author_id
        self.created_at = datetime.now()


class Discussion:


    def __init__(self, id: int, title: str, content: str, author: str, author_id: int):
        self.id = id
        self.title = title
        self.content = content
        self.author = author
        self.author_id = author_id
        self.created_at = datetime.now()


class DiscussionComment:


    def __init__(self, id: int, discussion_id: int, content: str, author: str, author_id: int):
        self.id = id
        self.discussion_id = discussion_id
        self.content = content
        self.author = author
        self.author_id = author_id
        self.created_at = datetime.now()
# 内存存储（用于数据迁移前的临时存储）
data_store = {
    "users": [],
    "stories": [],
    "chapters": [],
    "chapter_comments": [],
    "discussions": [],
    "discussion_comments": []
}
# 计数器
counters = {
    "user": 1,
    "story": 1,
    "chapter": 1,
    "chapter_comment": 1,
    "discussion": 1,
    "discussion_comment": 1
}


