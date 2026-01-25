from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_db
from crud import get_all_stories, get_all_discussions, get_user_by_id
from models import get_current_user
from sqlalchemy.orm import Session
from templates_config import templates
import markdown
import threading
import time
import atexit
from local_cache import local_cache
from database import SessionLocal

def generate_story_excerpt(content):
    """生成故事摘要"""
    # 分割为段落
    paragraphs = content.split('\n\n')
    if not paragraphs:
        return ''
    
    # 取第一段
    first_paragraph = paragraphs[0]
    
    # 按行分割
    lines = first_paragraph.split('\n')
    
    # 如果超过5行，只取前5行
    if len(lines) > 5:
        excerpt = '\n'.join(lines[:5]) + '...'
    else:
        excerpt = first_paragraph + '...'
    
    # 转换为HTML
    return markdown.markdown(excerpt)

# 定时同步函数
def sync_to_db_periodically():
    """每分钟同步一次数据到数据库"""
    while True:
        local_cache.sync_to_db()
        time.sleep(60)  # 每分钟同步一次

# 服务器关闭时的同步函数
def sync_on_shutdown():
    """服务器关闭时同步数据到数据库"""
    print("正在同步数据到数据库...")
    local_cache.sync_to_db()
    print("数据同步完成")

# 初始化本地缓存
def init_local_cache():
    """初始化本地缓存，从数据库加载数据"""
    db = SessionLocal()
    try:
        local_cache.load_from_db(db)
    finally:
        db.close()

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
# 初始化数据库 - 注释掉自动调用，避免消耗查询次数
# init_db()

# 初始化本地缓存
init_local_cache()

# 启动定时同步线程
sync_thread = threading.Thread(target=sync_to_db_periodically, daemon=True)
sync_thread.start()

# 注册服务器关闭时的同步函数
atexit.register(sync_on_shutdown)

# 包含路由
app.include_router(auth.router)
app.include_router(stories.router)
app.include_router(comments.router)
app.include_router(discussions.router)
app.include_router(admin.router)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    # 从本地缓存获取所有故事
    stories = get_all_stories(db)
    discussions = get_all_discussions(db)
    current_user = await get_current_user(request, db)
    
    # 为故事添加渲染内容
    story_with_authors = []
    for story in stories:
        # 从本地缓存获取作者
        author = get_user_by_id(db, story["author_id"])
        # 创建一个新的字典，添加作者名称
        story_dict = story.copy()
        story_dict["author_name"] = author["username"] if author else "未知作者"
        # 渲染故事摘要为HTML用于显示
        story_dict["content_html"] = generate_story_excerpt(story["content"])
        # 处理标签
        if isinstance(story["tags"], str):
            story_dict["tags"] = [tag.strip() for tag in story["tags"].split(',') if tag.strip()]
        elif not story["tags"]:
            story_dict["tags"] = []
        story_with_authors.append(story_dict)
    
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
