from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import (
    UserDB,
    StoryDB,
    StoryChapterDB,
    ChapterCommentDB,
    DiscussionDB,
    DiscussionCommentDB
)
# 用户相关操作


def create_user(db: Session, username: str, email: str, password_hash: str):
    """创建新用户"""
    db_user = UserDB(username=username, email=email, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_user_by_email(db: Session, email: str):
    """根据邮箱获取用户"""
    return db.query(UserDB).filter(UserDB.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """根据ID获取用户"""
    return db.query(UserDB).filter(UserDB.id == user_id).first()


def update_user_points(db: Session, user_id: int, points: int):
    """更新用户积分"""
    user = get_user_by_id(db, user_id)
    if user:
        user.points += points
        db.commit()
    return user


def update_user_active_count(db: Session, user_id: int):
    """更新用户活跃次数"""
    user = get_user_by_id(db, user_id)
    if user:
        user.active_count += 1
        db.commit()
    return user


def get_all_users(db: Session):
    """获取所有用户"""
    return db.query(UserDB).all()


def delete_user(db: Session, user_id: int):
    """删除用户"""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
# 故事相关操作


def create_story(db: Session, title: str, content: str, author_id: int):
    """创建新故事"""
    db_story = StoryDB(title=title, content=content, author_id=author_id)
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


def get_story_by_id(db: Session, story_id: int):
    """根据ID获取故事"""
    return db.query(StoryDB).filter(StoryDB.id == story_id).first()


def get_all_stories(db: Session):
    """获取所有故事"""
    return db.query(StoryDB).order_by(desc(StoryDB.created_at)).all()


def delete_story(db: Session, story_id: int):
    """删除故事"""
    story = get_story_by_id(db, story_id)
    if story:
        db.delete(story)
        db.commit()
        return True
    return False
# 章节相关操作


def create_chapter(db: Session, story_id: int, content: str, author_id: int, author_name: str):
    """创建新章节"""
    db_chapter = StoryChapterDB(
        story_id=story_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def get_chapters_by_story(db: Session, story_id: int):
    """获取故事的所有章节"""
    return db.query(StoryChapterDB)\
        .filter(StoryChapterDB.story_id == story_id)\
        .order_by(StoryChapterDB.created_at)\
        .all()


def get_chapter_by_id(db: Session, chapter_id: int):
    """根据ID获取章节"""
    return db.query(StoryChapterDB).filter(StoryChapterDB.id == chapter_id).first()


def delete_chapter(db: Session, chapter_id: int):
    """删除章节"""
    chapter = get_chapter_by_id(db, chapter_id)
    if chapter:
        db.delete(chapter)
        db.commit()
        return True
    return False
# 章节评论相关操作


def create_chapter_comment(db: Session, chapter_id: int, content: str, author_id: int, author_name: str):
    """创建章节评论"""
    db_comment = ChapterCommentDB(
        chapter_id=chapter_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_chapter(db: Session, chapter_id: int):
    """获取章节的所有评论"""
    return db.query(ChapterCommentDB)\
        .filter(ChapterCommentDB.chapter_id == chapter_id)\
        .order_by(ChapterCommentDB.created_at)\
        .all()


def delete_chapter_comment(db: Session, comment_id: int):
    """删除章节评论"""
    comment = db.query(ChapterCommentDB).filter(ChapterCommentDB.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return True
    return False
# 讨论主题相关操作


def create_discussion(db: Session, title: str, content: str, author_id: int, author_name: str):
    """创建讨论主题"""
    db_discussion = DiscussionDB(
        title=title,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    db.add(db_discussion)
    db.commit()
    db.refresh(db_discussion)
    return db_discussion


def get_all_discussions(db: Session):
    """获取所有讨论主题"""
    return db.query(DiscussionDB).order_by(desc(DiscussionDB.created_at)).all()


def get_discussion_by_id(db: Session, discussion_id: int):
    """根据ID获取讨论主题"""
    return db.query(DiscussionDB).filter(DiscussionDB.id == discussion_id).first()


def delete_discussion(db: Session, discussion_id: int):
    """删除讨论主题"""
    discussion = get_discussion_by_id(db, discussion_id)
    if discussion:
        db.delete(discussion)
        db.commit()
        return True
    return False
# 讨论评论相关操作


def create_discussion_comment(db: Session, discussion_id: int, content: str, author_id: int, author_name: str):
    """创建讨论评论"""
    db_comment = DiscussionCommentDB(
        discussion_id=discussion_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_discussion(db: Session, discussion_id: int):
    """获取讨论的所有评论"""
    return db.query(DiscussionCommentDB)\
        .filter(DiscussionCommentDB.discussion_id == discussion_id)\
        .order_by(DiscussionCommentDB.created_at)\
        .all()


def delete_discussion_comment(db: Session, comment_id: int):
    """删除讨论评论"""
    comment = db.query(DiscussionCommentDB).filter(DiscussionCommentDB.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return True
    return False
# 统计信息相关操作


def get_statistics(db: Session):
    """获取系统统计信息"""
    from sqlalchemy import func
    stats = {
        "total_users": db.query(func.count(UserDB.id)).scalar(),
        "total_stories": db.query(func.count(StoryDB.id)).scalar(),
        "total_chapters": db.query(func.count(StoryChapterDB.id)).scalar(),
        "total_discussions": db.query(func.count(DiscussionDB.id)).scalar(),
        "total_comments": (db.query(func.count(ChapterCommentDB.id)).scalar() + \
                          db.query(func.count(DiscussionCommentDB.id)).scalar()),
        "active_users": db.query(func.count(UserDB.id)).filter(UserDB.active_count > 0).scalar(),
        "recent_users": db.query(UserDB).order_by(desc(UserDB.registered_at)).limit(5).all(),
        "recent_stories": db.query(StoryDB).order_by(desc(StoryDB.created_at)).limit(5).all(),
        "recent_discussions": db.query(DiscussionDB).order_by(desc(DiscussionDB.created_at)).limit(5).all()
    }
    return stats


