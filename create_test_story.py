#!/usr/bin/env python3
"""
创建测试故事脚本
"""
import sys
import os
from datetime import datetime
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import get_db, StoryDB
from crud import create_story


def create_test_story():
    """创建测试故事"""
    db = next(get_db())
    try:
        # 获取测试用户
        from database import UserDB
        test_user = db.query(UserDB).filter(UserDB.username == "testuser").first()
        if not test_user:
            print("测试用户不存在")
            return None
        # 创建测试故事
        story = create_story(
            db=db,
            title="测试故事：神秘的森林",
            content="在一个遥远的地方，有一片神秘的森林。传说中，这片森林里住着各种神奇的生物，还有一个古老的秘密等待被发现...",
            author_id=test_user.id
        )
        print(f"测试故事创建成功！")
        print(f"故事ID: {story.id}")
        print(f"故事标题: {story.title}")
        print(f"作者: {test_user.username}")
        return story
    except Exception as e:
        print(f"创建测试故事失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()
if __name__ == "__main__":
    create_test_story()


