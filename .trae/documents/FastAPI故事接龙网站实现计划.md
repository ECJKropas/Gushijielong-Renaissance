# FastAPI故事接龙网站实现计划

## 项目结构设计
```
.
├── main.py                    # 主入口文件
├── models.py                  # 数据模型
├── routers/
│   ├── stories.py             # 故事相关路由
│   ├── comments.py            # 评论相关路由
│   └── discussions.py         # 讨论区相关路由
├── templates/
│   ├── base.html              # 基础模板
│   ├── index.html             # 首页
│   ├── story_detail.html      # 故事详情页
│   └── discussion.html        # 讨论区页面
└── static/
    ├── css/
    │   └── styles.css         # 样式文件
    └── js/
        └── scripts.js         # JavaScript文件
```

## 数据模型设计
1. **Story** - 故事模型
   - id: int
   - title: str
   - content: str
   - created_at: datetime
   - updated_at: datetime

2. **StoryChapter** - 故事章节（每层楼）
   - id: int
   - story_id: int
   - content: str
   - author: str
   - created_at: datetime

3. **ChapterComment** - 章节评论
   - id: int
   - chapter_id: int
   - content: str
   - author: str
   - created_at: datetime

4. **Discussion** - 讨论区主题
   - id: int
   - title: str
   - content: str
   - author: str
   - created_at: datetime

5. **DiscussionComment** - 讨论区评论
   - id: int
   - discussion_id: int
   - content: str
   - author: str
   - created_at: datetime

## 路由设计
- **GET /** - 首页，显示所有故事
- **GET /stories/{story_id}** - 故事详情页
- **POST /stories** - 创建新故事
- **POST /stories/{story_id}/chapters** - 添加故事章节
- **POST /chapters/{chapter_id}/comments** - 添加章节评论
- **GET /discussion** - 讨论区首页
- **POST /discussion** - 创建讨论主题
- **POST /discussion/{discussion_id}/comments** - 添加讨论评论

## 模板设计
1. **base.html** - 包含基本HTML结构、CSS和JavaScript引用
2. **index.html** - 继承base.html，显示故事列表
3. **story_detail.html** - 继承base.html，显示故事详情、章节列表、评论和讨论区
4. **discussion.html** - 继承base.html，显示讨论区主题列表

## 实现步骤
1. 创建项目基本结构
2. 实现数据模型
3. 实现主入口文件
4. 实现路由
5. 创建模板文件
6. 添加静态文件
7. 测试功能

## 技术栈
- FastAPI - Web框架
- Jinja2 - 模板引擎
- SQLite - 数据库（开发阶段）
- Pydantic - 数据验证
- SQLAlchemy - ORM（可选，可先使用简单的内存存储）