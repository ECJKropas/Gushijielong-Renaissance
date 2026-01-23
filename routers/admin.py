from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates_config import templates
from database import (
    get_db,
    UserDB,
    StoryDB,
    DiscussionDB,
    StoryChapterDB,
    ChapterCommentDB,
    DiscussionCommentDB
)
from crud import get_statistics, get_all_users, get_all_stories, get_all_discussions
from models import get_current_user
from sqlalchemy.orm import Session
router = APIRouter()
# 管理员权限检查


async def require_admin(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user or current_user.role != "admin":
        return None  # 返回None而不是抛出异常，让路由函数处理重定向
    return current_user
@router.get("/admin", response_class=HTMLResponse)


async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    stats = get_statistics(db)
    return templates.TemplateResponse(
        "admin_index.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats
        }
    )
@router.get("/admin/users", response_class=HTMLResponse)


async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    users = get_all_users(db)
    return templates.TemplateResponse(
        "admin_users.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users
        }
    )
@router.get("/admin/stories", response_class=HTMLResponse)


async def admin_stories(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    stories = get_all_stories(db)
    return templates.TemplateResponse(
        "admin_stories.html",
        {
            "request": request,
            "current_user": current_user,
            "stories": stories
        }
    )
@router.get("/admin/discussions", response_class=HTMLResponse)


async def admin_discussions(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    discussions = get_all_discussions(db)
    return templates.TemplateResponse(
        "admin_discussions.html",
        {
            "request": request,
            "current_user": current_user,
            "discussions": discussions
        }
    )
@router.post("/admin/delete/user/{user_id}")


async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # 不允许删除自己
    if user_id == current_user.id:
        return RedirectResponse(url="/admin/users", status_code=303)
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
@router.post("/admin/delete/story/{story_id}")


async def delete_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    story = db.query(StoryDB).filter(StoryDB.id == story_id).first()
    if story:
        # 删除相关的章节和评论
        db.query(StoryChapterDB).filter(StoryChapterDB.story_id == story_id).delete()
        db.query(ChapterCommentDB).filter(ChapterCommentDB.chapter_id.in_(
            db.query(StoryChapterDB.id).filter(StoryChapterDB.story_id == story_id)
        )).delete(synchronize_session=False)
        db.delete(story)
        db.commit()
    return RedirectResponse(url="/admin/stories", status_code=303)
@router.post("/admin/delete/discussion/{discussion_id}")


async def delete_discussion(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    discussion = db.query(DiscussionDB).filter(DiscussionDB.id == discussion_id).first()
    if discussion:
        # 删除相关的评论
        db.query(DiscussionCommentDB).filter(DiscussionCommentDB.discussion_id == discussion_id).delete()
        db.delete(discussion)
        db.commit()
    return RedirectResponse(url="/admin/discussions", status_code=303)
@router.post("/admin/make_admin/{user_id}")


async def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.role = "admin"
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)
@router.post("/admin/remove_admin/{user_id}")


async def remove_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_admin)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # 不允许移除自己的管理员权限
    if user_id == current_user.id:
        return RedirectResponse(url="/admin/users", status_code=303)
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user:
        user.role = "user"
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)


