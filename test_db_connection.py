#!/usr/bin/env python3
"""
测试数据库连接和功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, UserDB, StoryDB, DiscussionDB
from crud import get_statistics

def test_database():
    """测试数据库连接和功能"""
    print("=== 数据库连接测试 ===")
    
    try:
        db = next(get_db())
        print("✓ 数据库连接成功")
        
        # 测试用户查询
        users = db.query(UserDB).all()
        print(f"✓ 用户数量: {len(users)}")
        for user in users:
            print(f"  - {user.username} ({user.role}, 积分: {user.points})")
        
        # 测试故事查询
        stories = db.query(StoryDB).all()
        print(f"✓ 故事数量: {len(stories)}")
        for story in stories:
            print(f"  - {story.title} (作者ID: {story.author_id})")
        
        # 测试讨论查询
        discussions = db.query(DiscussionDB).all()
        print(f"✓ 讨论数量: {len(discussions)}")
        for discussion in discussions:
            print(f"  - {discussion.title} (作者: {discussion.author_name})")
        
        # 测试统计功能
        stats = get_statistics(db)
        print(f"\n=== 系统统计 ===")
        print(f"✓ 总用户数: {stats['total_users']}")
        print(f"✓ 总故事数: {stats['total_stories']}")
        print(f"✓ 总讨论数: {stats['total_discussions']}")
        print(f"✓ 管理员数: {stats['admin_count']}")
        
        db.close()
        print("\n✓ 所有数据库测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    test_database()