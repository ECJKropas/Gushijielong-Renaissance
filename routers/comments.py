from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from database import get_db, ChapterCommentDB
from crud import create_chapter_comment, update_user_active_count
from models import get_current_user
from sqlalchemy.orm import Session
router = APIRouter()
@router.post("/stories/{story_id}/chapters/{chapter_id}/comment")


async def add_chapter_comment(
    request: Request,
    story_id: int,
    chapter_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user(request)
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


