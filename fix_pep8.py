#!/usr/bin/env python3
"""
自动修复PEP 8问题的脚本
"""
import os
import re
# 定义要修复的文件类型
extensions = ['.py']
# 定义要跳过的目录
exclude_dirs = ['__pycache__', '.git', 'venv', '.venv']
# 修复行尾空格（W291）


def fix_trailing_whitespace(content):
    return re.sub(r'\s+$', '', content, flags=re.MULTILINE)
# 修复空行包含空格（W293）


def fix_blank_lines_with_spaces(content):
    return re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
# 确保文件末尾有一个空行（W292）


def fix_missing_newline_at_end(content):
    if content and not content.endswith('\n'):
        return content + '\n'
    return content
# 修复文件


def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content
    # 应用修复
    content = fix_trailing_whitespace(content)
    content = fix_blank_lines_with_spaces(content)
    content = fix_missing_newline_at_end(content)
    # 如果内容有变化，保存文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False
# 遍历目录并修复文件


def fix_directory(directory):
    fixed_files = 0
    for root, dirs, files in os.walk(directory):
        # 跳过排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if os.path.splitext(file)[1] in extensions:
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_files += 1
                    print(f"已修复: {file_path}")
    return fixed_files
if __name__ == "__main__":
    print("开始修复PEP 8问题...")
    fixed = fix_directory('.')
    print(f"修复完成！共修复了 {fixed} 个文件。")


