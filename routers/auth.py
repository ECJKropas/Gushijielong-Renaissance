from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from templates_config import templates
from database import get_db, UserDB
from crud import create_user, get_user_by_username, get_user_by_email, update_user_active_count
from sqlalchemy.orm import Session
import bcrypt
from local_cache import local_cache
router = APIRouter()
@router.get("/register", response_class=HTMLResponse)


async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
@router.post("/register")


async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 获取客户端IP地址
    client_ip = request.client.host if request.client else "unknown"
    # 检查IP注册频率限制
    if not local_cache.check_ip_rate_limit(client_ip):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "注册太过频繁，请5分钟后再试"}
        )
    # 检查用户名是否已存在
    if get_user_by_username(db, username):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "用户名已存在"}
        )
    # 检查邮箱是否已存在
    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "邮箱已存在"}
        )
    # 加密密码
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    # 创建新用户
    user = create_user(
        db=db,
        username=username,
        email=email,
        password_hash=password_hash
    )
    # 重定向到登录页面
    return RedirectResponse(url="/login", status_code=303)
@router.get("/login", response_class=HTMLResponse)


async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 查找用户
    user = get_user_by_username(db, username)
    # 验证密码
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "用户名或密码错误"}
        )
    # 更新用户活跃次数
    update_user_active_count(db, user["id"])
    # 设置登录cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user_id", value=str(user["id"]), httponly=True, max_age=86400)  # 24小时
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("user_id")
    return response


