from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from crud import get_all_stories, get_all_discussions
from models import get_current_user
from sqlalchemy.orm import Session
from templates_config import templates
import markdown
# 导入路由
from routers import stories, comments, discussions, auth, admin
# 创建FastAPI应用
app = FastAPI()
# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 配置静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")
# 初始化数据库
init_db()
# 包含路由
app.include_router(auth.router)
app.include_router(stories.router)
app.include_router(comments.router)
app.include_router(discussions.router)
app.include_router(admin.router)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    stories = get_all_stories(db)
    discussions = get_all_discussions(db)
    current_user = await get_current_user(request, db)
    
    # 为故事添加作者信息和渲染内容
    from crud import get_user_by_id
    story_with_authors = []
    for story in stories:
        author = get_user_by_id(db, story.author_id)
        story.author_name = author.username if author else "未知作者"
        # 渲染故事内容为HTML用于显示
        story.content_html = markdown.markdown(story.content)
        story_with_authors.append(story)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stories": story_with_authors,
            "discussions": discussions,
            "current_user": current_user
        }
    )
@app.get("/about", response_class=HTMLResponse)
async def read_about(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "current_user": current_user
        }
    )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


