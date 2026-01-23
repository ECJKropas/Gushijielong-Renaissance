#!/usr/bin/env python3
"""
数据迁移脚本 - 将内存数据迁移到SQLite数据库
"""
import os
import sys
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 导入数据库模型和CRUD操作
from database import (
    init_db, get_db, UserDB, StoryDB,
    StoryChapterDB, ChapterCommentDB,
    DiscussionDB, DiscussionCommentDB
)
from models import data_store


def migrate_data():
    """将内存数据迁移到数据库"""
    print("开始数据迁移...")
    # 初始化数据库
    init_db()
    # 获取数据库会话
    db = next(get_db())
    try:
        # 迁移用户数据
        print(f"正在迁移 {len(data_store['users'])} 个用户...")
        for user_data in data_store["users"]:
            try:
                # 检查用户是否已存在
                existing_user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
                if existing_user:
                    print(f"用户 {user_data.username} 已存在，跳过")
                    continue
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
                print(f"已迁移用户: {user_data.username}")
            except Exception as e:
                print(f"迁移用户 {user_data.username} 失败: {e}")
                continue
        # 迁移故事数据
        print(f"正在迁移 {len(data_store['stories'])} 个故事...")
        for story_data in data_store["stories"]:
            try:
                # 检查故事是否已存在
                existing_story = db.query(StoryDB).filter(StoryDB.id == story_data.id).first()
                if existing_story:
                    print(f"故事 {story_data.title} 已存在，跳过")
                    continue
                story = StoryDB(
                    id=story_data.id,
                    title=story_data.title,
                    content=story_data.content,
                    author_id=story_data.author_id,
                    created_at=story_data.created_at,
                    updated_at=story_data.updated_at
                )
                db.add(story)
                print(f"已迁移故事: {story_data.title}")
            except Exception as e:
                print(f"迁移故事 {story_data.title} 失败: {e}")
                continue
        # 迁移章节数据
        print(f"正在迁移 {len(data_store['chapters'])} 个章节...")
        for chapter_data in data_store["chapters"]:
            try:
                # 检查章节是否已存在
                existing_chapter = db.query(StoryChapterDB).filter(StoryChapterDB.id == chapter_data.id).first()
                if existing_chapter:
                    print(f"章节 {chapter_data.id} 已存在，跳过")
                    continue
                chapter = StoryChapterDB(
                    id=chapter_data.id,
                    story_id=chapter_data.story_id,
                    content=chapter_data.content,
                    author_id=chapter_data.author_id,
                    author_name=chapter_data.author,
                    created_at=chapter_data.created_at
                )
                db.add(chapter)
                print(f"已迁移章节: {chapter_data.id}")
            except Exception as e:
                print(f"迁移章节 {chapter_data.id} 失败: {e}")
                continue
        # 迁移章节评论数据
        print(f"正在迁移 {len(data_store['chapter_comments'])} 个章节评论...")
        for comment_data in data_store["chapter_comments"]:
            try:
                # 检查评论是否已存在
                existing_comment = db.query(ChapterCommentDB).filter(ChapterCommentDB.id == comment_data.id).first()
                if existing_comment:
                    print(f"章节评论 {comment_data.id} 已存在，跳过")
                    continue
                comment = ChapterCommentDB(
                    id=comment_data.id,
                    chapter_id=comment_data.chapter_id,
                    content=comment_data.content,
                    author_id=comment_data.author_id,
                    author_name=comment_data.author,
                    created_at=comment_data.created_at
                )
                db.add(comment)
                print(f"已迁移章节评论: {comment_data.id}")
            except Exception as e:
                print(f"迁移章节评论 {comment_data.id} 失败: {e}")
                continue
        # 迁移讨论数据
        print(f"正在迁移 {len(data_store['discussions'])} 个讨论...")
        for discussion_data in data_store["discussions"]:
            try:
                # 检查讨论是否已存在
                existing_discussion = db.query(DiscussionDB).filter(DiscussionDB.id == discussion_data.id).first()
                if existing_discussion:
                    print(f"讨论 {discussion_data.title} 已存在，跳过")
                    continue
                discussion = DiscussionDB(
                    id=discussion_data.id,
                    title=discussion_data.title,
                    content=discussion_data.content,
                    author_id=discussion_data.author_id,
                    author_name=discussion_data.author,
                    created_at=discussion_data.created_at
                )
                db.add(discussion)
                print(f"已迁移讨论: {discussion_data.title}")
            except Exception as e:
                print(f"迁移讨论 {discussion_data.title} 失败: {e}")
                continue
        # 迁移讨论评论数据
        print(f"正在迁移 {len(data_store['discussion_comments'])} 个讨论评论...")
        for comment_data in data_store["discussion_comments"]:
            try:
                # 检查评论是否已存在
                existing_comment = db.query(DiscussionCommentDB).filter(DiscussionCommentDB.id == comment_data.id).first()
                if existing_comment:
                    print(f"讨论评论 {comment_data.id} 已存在，跳过")
                    continue
                comment = DiscussionCommentDB(
                    id=comment_data.id,
                    discussion_id=comment_data.discussion_id,
                    content=comment_data.content,
                    author_id=comment_data.author_id,
                    author_name=comment_data.author,
                    created_at=comment_data.created_at
                )
                db.add(comment)
                print(f"已迁移讨论评论: {comment_data.id}")
            except Exception as e:
                print(f"迁移讨论评论 {comment_data.id} 失败: {e}")
                continue
        # 提交所有更改
        db.commit()
        print("数据迁移完成！")
        return True
    except Exception as e:
        print(f"数据迁移过程中发生错误: {e}")
        db.rollback()
        return False
    finally:
        db.close()
if __name__ == "__main__":
    migrate_data()


