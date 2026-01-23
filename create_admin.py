#!/usr/bin/env python3
"""
创建管理员用户脚本
"""
import sys
import os
from datetime import datetime
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import get_db, UserDB
import bcrypt


def create_admin_user():
    """创建管理员用户"""
    db = next(get_db())
    try:
        # 检查是否已存在管理员
        admin_user = db.query(UserDB).filter(UserDB.username == "admin").first()
        if admin_user:
            print("管理员用户已存在")
            return admin_user
        # 创建管理员用户
        password = "admin123"  # 默认密码
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        admin_user = UserDB(
            username="admin",
            email="admin@storychain.com",
            password_hash=password_hash,
            role="admin",
            registered_at=datetime.now(),
            active_count=0,
            points=1000,  # 管理员初始积分
            credit=100.0
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"管理员用户创建成功！")
        print(f"用户名: admin")
        print(f"密码: {password}")
        print(f"邮箱: admin@storychain.com")
        return admin_user
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()
if __name__ == "__main__":
    create_admin_user()


