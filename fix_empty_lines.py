#!/usr/bin/env python3
"""
自动修复函数定义前后空行的脚本
"""

import os
import re

# 定义要修复的文件类型
extensions = ['.py']

# 定义要跳过的目录
exclude_dirs = ['__pycache__', '.git', 'venv', '.venv']

# 修复函数定义前后的空行


def fix_function_empty_lines(content):
    # 匹配函数定义的正则表达式
    function_pattern = r'^\s*def\s+\w+\s*\(|^\s*async\s+def\s+\w+\s*\(|^\s*class\s+\w+'
    
    # 将内容按行分割
    lines = content.split('\n')
    
    # 记录函数定义的位置
    function_positions = []
    for i, line in enumerate(lines):
        if re.match(function_pattern, line):
            function_positions.append(i)
    
    if not function_positions:
        return '\n'.join(lines)
    
    # 修复第一个函数定义前的空行
    first_func = function_positions[0]
    # 删除现有的空行
    while first_func > 0 and not lines[first_func-1].strip():
        del lines[first_func-1]
        first_func -= 1
    # 添加两个空行
    lines.insert(first_func, '')
    lines.insert(first_func, '')
    
    # 调整后续函数位置（因为添加了空行）
    offset = 2
    for i in range(1, len(function_positions)):
        function_positions[i] += offset
    
    # 在函数定义前添加两个空行
    # 从后往前处理，避免位置偏移
    for i in reversed(function_positions[1:]):
        # 检查前一行是否为空行
        prev_empty = 0
        j = i - 1
        while j >= 0 and not lines[j].strip():
            prev_empty += 1
            j -= 1
        
        # 如果空行不足2个，添加到2个
        if prev_empty < 2:
            # 删除现有的空行
            while i > 0 and not lines[i-1].strip():
                del lines[i-1]
                i -= 1
            # 添加两个空行
            lines.insert(i, '')
            lines.insert(i, '')
    
    # 修复最后一个函数定义后的空行
    last_func = function_positions[-1]
    # 找到最后一个函数的结束位置
    last_func_end = last_func
    for i in range(last_func, len(lines)):
        if re.match(function_pattern, lines[i]):
            break
        last_func_end = i
    
    # 删除现有的空行
    j = last_func_end + 1
    while j < len(lines) and not lines[j].strip():
        del lines[j]
    # 添加两个空行
    lines.append('')
    lines.append('')
    
    return '\n'.join(lines)

# 修复文件


def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 应用修复
    content = fix_function_empty_lines(content)
    
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
    print("开始修复函数定义前后的空行...")
    fixed = fix_directory('.')
    print(f"修复完成！共修复了 {fixed} 个文件。")


