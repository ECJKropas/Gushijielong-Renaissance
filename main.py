from fastapi import FastAPI, Request, Depends, HTTPException
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
import logging
from enhanced_local_cache import enhanced_local_cache
from database_connection import db_manager, get_db_session
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 定时同步函数 - 增强版本
def sync_to_db_periodically():
    """每分钟同步一次数据到数据库，支持重连和回退"""
    retry_count = 0
    max_retries = 3
    
    while True:
        try:
            logger.info("开始定期数据同步...")
            
            # 尝试同步到数据库
            if enhanced_local_cache.sync_to_db_with_fallback():
                logger.info("定期数据同步成功")
                retry_count = 0  # 重置重试计数
            else:
                logger.warning("定期数据同步失败，使用临时存储")
                
        except Exception as e:
            logger.error(f"定期数据同步异常: {str(e)}")
            retry_count += 1
            
            if retry_count >= max_retries:
                logger.error("达到最大重试次数，暂停同步一段时间")
                time.sleep(300)  # 暂停5分钟
                retry_count = 0
                
        time.sleep(60)  # 每分钟同步一次

# 服务器关闭时的同步函数 - 增强版本
def sync_on_shutdown():
    """服务器关闭时同步数据到数据库，支持重连和回退"""
    logger.info("正在同步数据到数据库...")
    try:
        if enhanced_local_cache.sync_to_db_with_fallback():
            logger.info("数据同步完成")
        else:
            logger.warning("数据同步失败，数据已保存到临时存储")
    except Exception as e:
        logger.error(f"关闭时数据同步异常: {str(e)}")
        logger.warning("数据可能未完全同步，请检查临时存储")

# 初始化增强本地缓存
def init_enhanced_local_cache():
    """初始化增强本地缓存，支持数据库重连和临时存储回退"""
    logger.info("开始初始化增强本地缓存...")
    try:
        if enhanced_local_cache.load_from_db_with_fallback():
            logger.info("增强本地缓存初始化成功")
        else:
            logger.warning("增强本地缓存初始化失败，将使用空缓存启动")
            # 即使初始化失败也继续启动，避免应用无法启动
            
    except Exception as e:
        logger.error(f"增强本地缓存初始化异常: {str(e)}")
        logger.warning("将使用空缓存启动，数据库连接恢复后会自动同步数据")

# 导入路由
from routers import stories, comments, discussions, auth, admin, health, tree
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

# 初始化增强本地缓存
init_enhanced_local_cache()

# 启动增强的定时同步线程
logger.info("启动增强的定时同步线程...")
sync_thread = threading.Thread(target=sync_to_db_periodically, daemon=True, name="EnhancedSyncThread")
sync_thread.start()

# 注册服务器关闭时的同步函数
logger.info("注册关闭时的同步函数")
atexit.register(sync_on_shutdown)

# 包含路由
app.include_router(auth.router)
app.include_router(stories.router)
app.include_router(comments.router)
app.include_router(discussions.router)
app.include_router(admin.router)
app.include_router(health.router)
app.include_router(tree.router)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """增强的根路由，支持数据库连接问题时的优雅降级"""
    try:
        # 检查数据库连接状态
        if not enhanced_local_cache.is_db_available():
            logger.warning("数据库连接不可用，使用本地缓存数据")
            
        # 从增强本地缓存获取数据
        stories_data = enhanced_local_cache.data.get("stories", {})
        discussions_data = enhanced_local_cache.data.get("discussions", {})
        
        # 转换数据格式
        stories = list(stories_data.values())
        discussions = list(discussions_data.values())
        
        # 尝试获取当前用户信息
        current_user = None
        try:
            current_user = await get_current_user(request, db)
        except Exception as e:
            logger.warning(f"获取用户信息失败: {str(e)}")
            # 继续处理，即使用户信息获取失败
            
        # 生成故事摘要
        for story in stories:
            if 'content' in story:
                story['excerpt'] = generate_story_excerpt(story['content'])
                
        return templates.TemplateResponse("index.html", {
            "request": request,
            "stories": stories,
            "discussions": discussions,
            "current_user": current_user
        })
        
    except Exception as e:
        logger.error(f"处理根路由请求失败: {str(e)}")
        # 返回一个基本的错误页面
        return HTMLResponse(content=f"""
        <html>
        <head><title>服务暂时不可用</title></head>
        <body>
            <h1>服务暂时不可用</h1>
            <p>我们正在努力恢复服务，请稍后再试。</p>
            <p>错误信息: {str(e)}</p>
        </body>
        </html>
        """, status_code=503)
    
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
