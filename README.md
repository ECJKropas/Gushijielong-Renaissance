# 故事接龙网站 - SQLite数据存储版本

## 项目概述

这是一个基于FastAPI和SQLite的故事接龙网站，支持用户注册、登录、创建故事、添加章节、参与讨论等功能。所有数据现在都存储在SQLite数据库中，实现了数据持久化。

## 主要功能

### 1. 用户系统
- 用户注册（使用bcrypt密码加密）
- 用户登录/登出
- 用户权限管理（普通用户/管理员）
- 用户积分、信用点、活跃次数统计

### 2. 故事系统
- 创建新故事
- 查看故事详情
- 为故事添加续写章节
- 章节评论功能

### 3. 讨论系统
- 创建讨论主题
- 查看讨论详情
- 参与讨论评论

### 4. 管理后台（临时功能）
- 数据概览仪表盘
- 用户管理（查看、删除、权限设置）
- 故事管理（查看、删除）
- 讨论管理（查看、删除）

## 技术架构

### 后端技术
- **FastAPI**: Web框架
- **SQLAlchemy**: ORM框架
- **SQLite**: 数据库
- **bcrypt**: 密码加密
- **Jinja2**: 模板引擎

### 前端技术
- **HTML5/CSS3**: 页面结构和样式
- **JavaScript**: 交互功能
- **Bootstrap**: UI框架

### 数据库设计

#### 用户表 (users)
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希
- role: 角色（user/admin）
- registered_at: 注册时间
- active_count: 活跃次数
- points: 积分
- credit: 信用点

#### 故事表 (stories)
- id: 主键
- title: 标题
- content: 内容
- author_id: 作者ID（外键）
- created_at: 创建时间
- updated_at: 更新时间

#### 章节表 (story_chapters)
- id: 主键
- story_id: 故事ID（外键）
- content: 内容
- author_id: 作者ID（外键）
- author_name: 作者名
- created_at: 创建时间

#### 章节评论表 (chapter_comments)
- id: 主键
- chapter_id: 章节ID（外键）
- content: 内容
- author_id: 作者ID（外键）
- author_name: 作者名
- created_at: 创建时间

#### 讨论表 (discussions)
- id: 主键
- title: 标题
- content: 内容
- author_id: 作者ID（外键）
- author_name: 作者名
- created_at: 创建时间

#### 讨论评论表 (discussion_comments)
- id: 主键
- discussion_id: 讨论ID（外键）
- content: 内容
- author_id: 作者ID（外键）
- author_name: 作者名
- created_at: 创建时间

## 安装和运行

### 1. 安装依赖
```bash
pip install fastapi uvicorn jinja2 sqlalchemy bcrypt
```

### 2. 运行服务器
```bash
python main.py
```

服务器将在 http://127.0.0.1:8000 启动

### 3. 管理员账户
- 用户名: `admin`
- 密码: `admin123`
- 管理后台: http://127.0.0.1:8000/admin

### 4. 测试用户
- 用户名: `testuser`
- 密码: `test123`

## 数据持久化

所有数据现在都存储在SQLite数据库中，文件名为`story_chain.db`。数据库会在首次运行时自动创建，包含所有必要的表结构。

### 数据迁移

如果需要从旧版本迁移数据，可以运行：
```bash
python migrate_data.py
```

## 管理功能说明

管理后台是一个临时功能，用于数据管理和系统监控，包含以下功能：

### 仪表盘
- 显示系统概览统计
- 最近注册用户
- 最近创建的故事和讨论

### 用户管理
- 查看所有用户信息
- 设置/移除管理员权限
- 删除用户（不能删除自己）

### 故事管理
- 查看所有故事
- 删除故事（会同时删除相关章节和评论）

### 讨论管理
- 查看所有讨论
- 删除讨论（会同时删除相关评论）

## 文件结构

```
story-chain-website/
├── main.py                 # 主程序
├── database.py             # 数据库模型和连接
├── crud.py                 # 数据库操作函数
├── models.py               # 数据模型定义
├── templates_config.py     # 模板配置
├── migrate_data.py         # 数据迁移脚本
├── create_admin.py         # 创建管理员脚本
├── create_test_user.py     # 创建测试用户脚本
├── create_test_story.py    # 创建测试故事脚本
├── requirements.txt        # 项目依赖
├── story_chain.db          # SQLite数据库文件
├── routers/                # 路由模块
│   ├── __init__.py
│   ├── auth.py            # 认证路由
│   ├── stories.py         # 故事路由
│   ├── discussions.py     # 讨论路由
│   ├── comments.py        # 评论路由
│   └── admin.py           # 管理后台路由
├── templates/             # HTML模板
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── stories.html
│   ├── story_detail.html
│   ├── create_story.html
│   ├── discussions.html
│   ├── discussion_detail.html
│   ├── create_discussion.html
│   ├── about.html
│   └── admin_*.html       # 管理后台模板
└── static/                # 静态文件
    ├── css/
    │   └── styles.css
    └── js/
        └── scripts.js
```

## 注意事项

1. **管理员权限**: 管理后台需要管理员权限才能访问，请妥善保管管理员账户信息
2. **数据备份**: 定期备份`story_chain.db`文件以防数据丢失
3. **密码安全**: 用户密码使用bcrypt加密存储，安全可靠
4. **会话管理**: 使用cookie进行用户会话管理，有效期24小时

## 后续优化建议

1. **数据库优化**: 考虑使用PostgreSQL等更强大的数据库
2. **缓存系统**: 添加Redis缓存提高性能
3. **文件上传**: 支持用户头像、故事配图等功能
4. **富文本编辑器**: 改进内容编辑体验
5. **搜索功能**: 添加全文搜索功能
6. **API文档**: 使用FastAPI自动生成API文档
7. **测试覆盖**: 添加单元测试和集成测试

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: admin@storychain.com
- 项目地址: https://github.com/yourusername/story-chain-website