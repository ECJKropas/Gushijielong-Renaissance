#!/usr/bin/env python3
"""
创建测试用户脚本
"""
import sys
import os
from datetime import datetime
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import get_db, UserDB
import bcrypt


def create_test_user():
    """创建测试用户"""
    db = next(get_db())
    try:
        # 创建测试用户
        username = "testuser"
        email = "test@example.com"
        password = "test123"
        # 检查是否已存在
        existing_user = db.query(UserDB).filter(UserDB.username == username).first()
        if existing_user:
            print("测试用户已存在")
            return existing_user
        # 创建密码哈希
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        test_user = UserDB(
            username=username,
            email=email,
            password_hash=password_hash,
            role="user",
            registered_at=datetime.now(),
            active_count=0,
            points=100,
            credit=95.0
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"测试用户创建成功！")
        print(f"用户名: {username}")
        print(f"密码: {password}")
        print(f"邮箱: {email}")
        return test_user
    except Exception as e:
        print(f"创建测试用户失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()
if __name__ == "__main__":
    create_test_user()


