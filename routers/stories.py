from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from models import get_current_user
from templates_config import templates
from database import get_db, StoryDB, StoryChapterDB, ChapterCommentDB
from crud import (
    create_story,
    get_story_by_id,
    get_chapters_by_story,
    create_chapter,
    create_chapter_comment,
    get_comments_by_chapter,
    update_user_active_count,
    get_all_stories
)
from sqlalchemy.orm import Session
import markdown
router = APIRouter()
@router.get("/stories/{story_id}", response_class=HTMLResponse)


async def read_story(request: Request, story_id: int, db: Session = Depends(get_db)):
    story = get_story_by_id(db, story_id)
    if not story:
        return RedirectResponse(url="/")
    
    # 获取故事作者
    from crud import get_user_by_id
    story_author = get_user_by_id(db, story.author_id)
    story_author_name = story_author.username if story_author else "未知作者"
    
    # 渲染故事内容为HTML
    story.content_html = markdown.markdown(story.content)
    
    chapters = get_chapters_by_story(db, story_id)
    chapter_comments = {}
    for chapter in chapters:
        # 渲染章节内容为HTML
        chapter.content_html = markdown.markdown(chapter.content)
        # 获取章节评论
        comments = get_comments_by_chapter(db, chapter.id)
        # 渲染评论内容为HTML
        for comment in comments:
            comment.content_html = markdown.markdown(comment.content)
        chapter_comments[chapter.id] = comments
    
    # 获取讨论数据
    from crud import get_all_discussions
    discussions = get_all_discussions(db)
    
    current_user = await get_current_user(request, db)
    return templates.TemplateResponse(
        "story_detail.html",
        {
            "request": request,
            "story": story,
            "story_author_name": story_author_name,
            "chapters": chapters,
            "chapter_comments": chapter_comments,
            "discussions": discussions,
            "current_user": current_user
        }
    )
@router.post("/stories/{story_id}/chapters")


async def continue_story(
    request: Request,
    story_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    story = get_story_by_id(db, story_id)
    if not story:
        return RedirectResponse(url="/", status_code=303)
    # 创建新章节
    chapter = create_chapter(
        db=db,
        story_id=story_id,
        content=content,
        author_id=current_user.id,
        author_name=current_user.username
    )
    # 更新用户活跃次数
    update_user_active_count(db, current_user.id)
    return RedirectResponse(url=f"/stories/{story_id}", status_code=303)
@router.post("/stories/{story_id}/chapters/{chapter_id}/comment")


async def add_chapter_comment(
    request: Request,
    story_id: int,
    chapter_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # 创建评论
    create_chapter_comment(
        db=db,
        chapter_id=chapter_id,
        content=content,
        author_id=current_user.id,
        author_name=current_user.username
    )
    # 更新用户活跃次数
    update_user_active_count(db, current_user.id)
    return RedirectResponse(url=f"/stories/{story_id}#{chapter_id}", status_code=303)
@router.get("/stories", response_class=HTMLResponse)


async def list_stories(request: Request, db: Session = Depends(get_db)):
    # 重定向到首页，因为首页已经包含了故事列表功能
    return RedirectResponse(url="/", status_code=303)
@router.get("/create-story", response_class=HTMLResponse)


async def create_story_form(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        "create_story.html",
        {"request": request, "current_user": current_user}
    )
@router.post("/create-story")


async def create_new_story(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # 创建新故事
    story = create_story(
        db=db,
        title=title,
        content=content,
        author_id=current_user.id
    )
    # 更新用户活跃次数
    update_user_active_count(db, current_user.id)
    return RedirectResponse(url=f"/stories/{story.id}", status_code=303)


