#!/usr/bin/env python3
"""
测试管理员访问功能
"""
import requests
import sys


def test_admin_access():
    """测试管理员访问"""
    base_url = "http://127.0.0.1:8000"
    # 1. 测试未登录访问管理页面
    try:
        response = requests.get(f"{base_url}/admin")
        print(f"未登录访问管理页面: {response.status_code}")
        if response.status_code == 403:
            print("✓ 正确拒绝了未授权访问")
        else:
            print(f"✗ 意外的状态码: {response.status_code}")
    except Exception as e:
        print(f"✗ 访问失败: {e}")
    # 2. 测试登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    session = requests.Session()
    try:
        # 登录
        response = session.post(f"{base_url}/login", data=login_data)
        print(f"\n管理员登录: {response.status_code}")
        if response.status_code == 200:
            print("✓ 登录成功")
            # 3. 测试已登录访问管理页面
            response = session.get(f"{base_url}/admin")
            print(f"已登录访问管理页面: {response.status_code}")
            if response.status_code == 200:
                print("✓ 成功访问管理页面")
                # 4. 测试用户管理页面
                response = session.get(f"{base_url}/admin/users")
                print(f"访问用户管理页面: {response.status_code}")
                if response.status_code == 200:
                    print("✓ 成功访问用户管理页面")
                else:
                    print(f"✗ 访问用户管理页面失败: {response.status_code}")
            else:
                print(f"✗ 访问管理页面失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
        else:
            print(f"✗ 登录失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
if __name__ == "__main__":
    test_admin_access()


