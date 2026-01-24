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
from local_cache import local_cache
# 用户相关操作


def create_user(db: Session, username: str, email: str, password_hash: str):
    """创建新用户"""
    # 先获取最大ID
    users = local_cache.get_all("users")
    max_id = max([user.id for user in users]) if users else 0
    
    # 创建新用户
    db_user = UserDB(
        id=max_id + 1,
        username=username,
        email=email,
        password_hash=password_hash
    )
    
    # 添加到本地缓存
    local_cache.add("users", db_user)
    
    return db_user


def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    # 从本地缓存获取
    users = local_cache.get_all("users")
    for user in users:
        if user.username == username:
            return user
    return None


def get_user_by_email(db: Session, email: str):
    """根据邮箱获取用户"""
    # 从本地缓存获取
    users = local_cache.get_all("users")
    for user in users:
        if user.email == email:
            return user
    return None


def get_user_by_id(db: Session, user_id: int):
    """根据ID获取用户"""
    # 从本地缓存获取
    return local_cache.get("users", user_id)


def update_user_points(db: Session, user_id: int, points: int):
    """更新用户积分"""
    user = local_cache.get("users", user_id)
    if user:
        # 确保points不为None
        if user.points is None:
            user.points = 0
        user.points += points
        local_cache.update("users", user)
    return user


def update_user_active_count(db: Session, user_id: int):
    """更新用户活跃次数"""
    user = local_cache.get("users", user_id)
    if user:
        # 确保active_count不为None
        if user.active_count is None:
            user.active_count = 0
        user.active_count += 1
        local_cache.update("users", user)
    return user


def get_all_users(db: Session):
    """获取所有用户"""
    # 从本地缓存获取
    return local_cache.get_all("users")


def delete_user(db: Session, user_id: int):
    """删除用户"""
    # 从本地缓存删除
    return local_cache.delete("users", user_id)

# 故事相关操作


def create_story(db: Session, title: str, content: str, author_id: int, tags: str = ""):
    """创建新故事"""
    # 先获取最大ID
    stories = local_cache.get_all("stories")
    max_id = max([story.id for story in stories]) if stories else 0
    
    # 创建新故事
    db_story = StoryDB(
        id=max_id + 1,
        title=title,
        content=content,
        author_id=author_id,
        tags=tags
    )
    
    # 添加到本地缓存
    local_cache.add("stories", db_story)
    
    return db_story


def get_story_by_id(db: Session, story_id: int):
    """根据ID获取故事"""
    # 从本地缓存获取
    return local_cache.get("stories", story_id)


def get_all_stories(db: Session):
    """获取所有故事"""
    # 从本地缓存获取
    stories = local_cache.get_all("stories")
    # 按创建时间倒序排列
    return sorted(stories, key=lambda x: x.created_at, reverse=True)


def delete_story(db: Session, story_id: int):
    """删除故事，包括相关章节和评论"""
    # 从本地缓存获取故事
    story = local_cache.get("stories", story_id)
    if story:
        # 先获取所有相关章节
        chapters = local_cache.get_all("story_chapters")
        chapter_ids = [chapter.id for chapter in chapters if chapter.story_id == story_id]
        
        # 删除相关评论
        for chapter_id in chapter_ids:
            comments = local_cache.get_all("chapter_comments")
            for comment in comments:
                if comment.chapter_id == chapter_id:
                    local_cache.delete("chapter_comments", comment.id)
        
        # 删除相关章节
        for chapter_id in chapter_ids:
            local_cache.delete("story_chapters", chapter_id)
        
        # 删除故事
        local_cache.delete("stories", story_id)
        return True
    return False

# 章节相关操作


def create_chapter(db: Session, story_id: int, content: str, author_id: int, author_name: str):
    """创建新章节"""
    # 先获取最大ID
    chapters = local_cache.get_all("story_chapters")
    max_id = max([chapter.id for chapter in chapters]) if chapters else 0
    
    # 创建新章节
    db_chapter = StoryChapterDB(
        id=max_id + 1,
        story_id=story_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    
    # 添加到本地缓存
    local_cache.add("story_chapters", db_chapter)
    
    return db_chapter


def get_chapters_by_story(db: Session, story_id: int):
    """获取故事的所有章节"""
    # 从本地缓存获取
    chapters = local_cache.get_all("story_chapters")
    # 筛选出指定故事的章节并按创建时间排序
    return sorted(
        [chapter for chapter in chapters if chapter.story_id == story_id],
        key=lambda x: x.created_at
    )


def get_chapter_by_id(db: Session, chapter_id: int):
    """根据ID获取章节"""
    # 从本地缓存获取
    return local_cache.get("story_chapters", chapter_id)


def delete_chapter(db: Session, chapter_id: int):
    """删除章节，包括相关评论"""
    # 从本地缓存获取章节
    chapter = local_cache.get("story_chapters", chapter_id)
    if chapter:
        # 删除相关评论
        comments = local_cache.get_all("chapter_comments")
        for comment in comments:
            if comment.chapter_id == chapter_id:
                local_cache.delete("chapter_comments", comment.id)
        
        # 删除章节
        local_cache.delete("story_chapters", chapter_id)
        return True
    return False

# 章节评论相关操作


def create_chapter_comment(db: Session, chapter_id: int, content: str, author_id: int, author_name: str):
    """创建章节评论"""
    # 先获取最大ID
    comments = local_cache.get_all("chapter_comments")
    max_id = max([comment.id for comment in comments]) if comments else 0
    
    # 创建新评论
    db_comment = ChapterCommentDB(
        id=max_id + 1,
        chapter_id=chapter_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    
    # 添加到本地缓存
    local_cache.add("chapter_comments", db_comment)
    
    return db_comment


def get_comments_by_chapter(db: Session, chapter_id: int):
    """获取章节的所有评论"""
    # 从本地缓存获取
    comments = local_cache.get_all("chapter_comments")
    # 筛选出指定章节的评论并按创建时间排序
    return sorted(
        [comment for comment in comments if comment.chapter_id == chapter_id],
        key=lambda x: x.created_at
    )


def delete_chapter_comment(db: Session, comment_id: int):
    """删除章节评论"""
    # 从本地缓存删除
    return local_cache.delete("chapter_comments", comment_id)

# 讨论主题相关操作


def create_discussion(db: Session, title: str, content: str, author_id: int, author_name: str):
    """创建讨论主题"""
    # 先获取最大ID
    discussions = local_cache.get_all("discussions")
    max_id = max([discussion.id for discussion in discussions]) if discussions else 0
    
    # 创建新讨论
    db_discussion = DiscussionDB(
        id=max_id + 1,
        title=title,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    
    # 添加到本地缓存
    local_cache.add("discussions", db_discussion)
    
    return db_discussion


def get_all_discussions(db: Session):
    """获取所有讨论主题"""
    # 从本地缓存获取
    discussions = local_cache.get_all("discussions")
    # 按创建时间倒序排列
    return sorted(discussions, key=lambda x: x.created_at, reverse=True)


def get_discussion_by_id(db: Session, discussion_id: int):
    """根据ID获取讨论主题"""
    # 从本地缓存获取
    return local_cache.get("discussions", discussion_id)


def delete_discussion(db: Session, discussion_id: int):
    """删除讨论主题，包括相关评论"""
    # 从本地缓存获取讨论
    discussion = local_cache.get("discussions", discussion_id)
    if discussion:
        # 删除相关评论
        comments = local_cache.get_all("discussion_comments")
        for comment in comments:
            if comment.discussion_id == discussion_id:
                local_cache.delete("discussion_comments", comment.id)
        
        # 删除讨论
        local_cache.delete("discussions", discussion_id)
        return True
    return False

# 讨论评论相关操作


def create_discussion_comment(db: Session, discussion_id: int, content: str, author_id: int, author_name: str):
    """创建讨论评论"""
    # 先获取最大ID
    comments = local_cache.get_all("discussion_comments")
    max_id = max([comment.id for comment in comments]) if comments else 0
    
    # 创建新评论
    db_comment = DiscussionCommentDB(
        id=max_id + 1,
        discussion_id=discussion_id,
        content=content,
        author_id=author_id,
        author_name=author_name
    )
    
    # 添加到本地缓存
    local_cache.add("discussion_comments", db_comment)
    
    return db_comment


def get_comments_by_discussion(db: Session, discussion_id: int):
    """获取讨论的所有评论"""
    # 从本地缓存获取
    comments = local_cache.get_all("discussion_comments")
    # 筛选出指定讨论的评论并按创建时间排序
    return sorted(
        [comment for comment in comments if comment.discussion_id == discussion_id],
        key=lambda x: x.created_at
    )


def delete_discussion_comment(db: Session, comment_id: int):
    """删除讨论评论"""
    # 从本地缓存删除
    return local_cache.delete("discussion_comments", comment_id)

# 统计信息相关操作


def get_statistics(db: Session):
    """获取系统统计信息"""
    from sqlalchemy import func
    
    # 从本地缓存获取数据
    users = local_cache.get_all("users")
    stories = local_cache.get_all("stories")
    chapters = local_cache.get_all("story_chapters")
    discussions = local_cache.get_all("discussions")
    chapter_comments = local_cache.get_all("chapter_comments")
    discussion_comments = local_cache.get_all("discussion_comments")
    
    # 计算统计信息
    total_users = len(users)
    total_stories = len(stories)
    total_chapters = len(chapters)
    total_discussions = len(discussions)
    total_chapter_comments = len(chapter_comments)
    total_discussion_comments = len(discussion_comments)
    # 确保只处理active_count不为None的情况
    active_users = len([user for user in users if user.active_count is not None and user.active_count > 0])
    
    # 获取最近的用户、故事和讨论
    recent_users = sorted(users, key=lambda x: x.registered_at, reverse=True)[:5]
    recent_stories = sorted(stories, key=lambda x: x.created_at, reverse=True)[:5]
    recent_discussions = sorted(discussions, key=lambda x: x.created_at, reverse=True)[:5]
    
    stats = {
        "total_users": total_users,
        "total_stories": total_stories,
        "total_chapters": total_chapters,
        "total_discussions": total_discussions,
        "total_comments": total_chapter_comments + total_discussion_comments,
        "active_users": active_users,
        "recent_users": recent_users,
        "recent_stories": recent_stories,
        "recent_discussions": recent_discussions
    }
    return stats
