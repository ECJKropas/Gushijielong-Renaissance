#!/usr/bin/env python3
"""
测试添加章节功能
"""

import requests

# 测试添加章节功能

def test_add_chapter():
    print("测试添加章节功能...")
    
    # 首先需要登录获取cookie
    login_url = "http://localhost:8000/login"
    login_data = {
        "username": "admin_test",
        "password": "test123"
    }
    
    # 创建会话对象，用于保持cookie
    session = requests.Session()
    # 禁用代理
    session.proxies = {}
    
    # 发送登录请求
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    print(f"登录请求状态码: {login_response.status_code}")
    
    # 检查是否登录成功
    if "user_id" in session.cookies:
        print("登录成功，获取到user_id cookie")
        
        # 测试添加章节
        # 假设已经有一个故事，ID为1
        story_id = 1
        add_chapter_url = f"http://localhost:8000/stories/{story_id}/chapters"
        chapter_data = {
            "content": "这是测试添加的章节内容"
        }
        
        # 发送添加章节请求
        add_chapter_response = session.post(add_chapter_url, data=chapter_data, allow_redirects=True)
        print(f"添加章节请求状态码: {add_chapter_response.status_code}")
        
        if add_chapter_response.status_code == 303:
            print("添加章节成功！服务器返回303重定向")
            print(f"重定向到: {add_chapter_response.headers['location']}")
            return True
        else:
            print(f"添加章节失败，状态码: {add_chapter_response.status_code}")
            print(f"响应内容: {add_chapter_response.text}")
            return False
    else:
        print("登录失败，未获取到user_id cookie")
        return False

if __name__ == "__main__":
    test_add_chapter()
