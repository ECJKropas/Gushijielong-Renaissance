#!/usr/bin/env python3
"""
创建admin账户脚本
"""

import bcrypt
from database import SessionLocal, UserDB

# 创建数据库会话
db = SessionLocal()

try:
    # 检查admin用户是否已存在
    existing_admin = db.query(UserDB).filter(UserDB.username == "admin").first()
    if existing_admin:
        print("admin用户已存在")
    else:
        # 加密密码
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # 创建admin用户
        admin_user = UserDB(
            username="admin",
            email="admin@example.com",
            password_hash=password_hash,
            role="admin"
        )
        
        # 添加到数据库
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"admin用户创建成功，ID: {admin_user.id}")
finally:
    # 关闭数据库会话
    db.close()
