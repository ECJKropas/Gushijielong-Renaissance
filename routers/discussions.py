from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from models import get_current_user
from templates_config import templates
from database import get_db, DiscussionDB, DiscussionCommentDB
from crud import (
    create_discussion,
    get_all_discussions,
    get_discussion_by_id,
    create_discussion_comment,
    get_comments_by_discussion,
    update_user_active_count
)
from sqlalchemy.orm import Session
import markdown
router = APIRouter()
@router.get("/discussions", response_class=HTMLResponse)


async def list_discussions(request: Request, db: Session = Depends(get_db)):
    discussions = get_all_discussions(db)
    # 获取所有讨论的评论
    discussion_comments = {}
    for discussion in discussions:
        # 渲染讨论内容为HTML
        discussion.content_html = markdown.markdown(discussion.content)
        comments = get_comments_by_discussion(db, discussion.id)
        # 渲染评论内容为HTML
        for comment in comments:
            comment.content_html = markdown.markdown(comment.content)
        discussion_comments[discussion.id] = comments
    current_user = await get_current_user(request, db)
    return templates.TemplateResponse(
        "discussions.html",
        {
            "request": request,
            "discussions": discussions,
            "discussion_comments": discussion_comments,
            "current_user": current_user
        }
    )
@router.get("/discussions/{discussion_id}", response_class=HTMLResponse)


async def read_discussion(request: Request, discussion_id: int, db: Session = Depends(get_db)):
    discussion = get_discussion_by_id(db, discussion_id)
    if not discussion:
        return RedirectResponse(url="/discussions", status_code=303)
    # 渲染讨论内容为HTML
    discussion.content_html = markdown.markdown(discussion.content)
    comments = get_comments_by_discussion(db, discussion_id)
    # 渲染评论内容为HTML
    for comment in comments:
        comment.content_html = markdown.markdown(comment.content)
    current_user = await get_current_user(request, db)
    return templates.TemplateResponse(
        "discussion_detail.html",
        {
            "request": request,
            "discussion": discussion,
            "comments": comments,
            "current_user": current_user
        }
    )
@router.get("/create-discussion", response_class=HTMLResponse)


async def create_discussion_form(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "create_discussion.html",
        {"request": request, "current_user": current_user}
    )
@router.post("/create-discussion")


async def create_new_discussion(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # 创建新讨论
    discussion = create_discussion(
        db=db,
        title=title,
        content=content,
        author_id=current_user.id,
        author_name=current_user.username
    )
    # 更新用户活跃次数
    update_user_active_count(db, current_user.id)
    return RedirectResponse(url=f"/discussions/{discussion.id}", status_code=303)
@router.post("/discussions/{discussion_id}/comment")


async def add_discussion_comment(
    request: Request,
    discussion_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    discussion = get_discussion_by_id(db, discussion_id)
    if not discussion:
        return RedirectResponse(url="/discussions", status_code=303)
    # 创建评论
    create_discussion_comment(
        db=db,
        discussion_id=discussion_id,
        content=content,
        author_id=current_user.id,
        author_name=current_user.username
    )
    # 更新用户活跃次数
    update_user_active_count(db, current_user.id)
    return RedirectResponse(url=f"/discussions/{discussion_id}", status_code=303)


