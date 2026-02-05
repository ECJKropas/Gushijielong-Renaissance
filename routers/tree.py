from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database import get_db
from models import get_current_user, StoryTreeNode, counters, data_store
from enhanced_local_cache import enhanced_local_cache
import markdown
from datetime import datetime
from templates_config import templates

router = APIRouter()

# 获取起始节点列表（parent_id为None的节点）
def get_root_nodes():
    nodes = []
    for node_id, node_data in enhanced_local_cache.data.get("story_tree_nodes", {}).items():
        if node_data.get("parent_id") is None:
            nodes.append(node_data)
    return nodes

# 获取以指定节点为根的故事树
def get_story_tree(node_id):
    # 先检查缓存中是否存在完整的树结构
    cached_tree = enhanced_local_cache.data.get("cached_trees", {}).get(node_id)
    if cached_tree:
        return cached_tree
    
    tree = {}
    
    # 首先获取根节点
    root_node = enhanced_local_cache.data.get("story_tree_nodes", {}).get(node_id)
    if not root_node:
        return None
    
    # 构建树结构
    tree[node_id] = {
        "id": root_node["id"],
        "title": root_node["title"],
        "option_title": root_node["option_title"],
        "content": root_node["content"],
        "parent_id": root_node["parent_id"],
        "author_id": root_node["author_id"],
        "created_at": root_node["created_at"],
        "children": []
    }
    
    # 递归获取子节点
    def get_children(parent_id, parent_node):
        for child_id, child_data in enhanced_local_cache.data.get("story_tree_nodes", {}).items():
            if child_data.get("parent_id") == parent_id:
                child_node = {
                    "id": child_data["id"],
                    "title": child_data["title"],
                    "option_title": child_data["option_title"],
                    "content": child_data["content"],
                    "parent_id": child_data["parent_id"],
                    "author_id": child_data["author_id"],
                    "created_at": child_data["created_at"],
                    "children": []
                }
                parent_node["children"].append(child_node)
                get_children(child_id, child_node)
    
    get_children(node_id, tree[node_id])
    
    # 缓存树结构，避免重复计算
    if "cached_trees" not in enhanced_local_cache.data:
        enhanced_local_cache.data["cached_trees"] = {}
    enhanced_local_cache.data["cached_trees"][node_id] = tree
    
    return tree

# 显示起始节点列表
@router.get("/tree", response_class=HTMLResponse)
async def get_tree_root(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    root_nodes = get_root_nodes()
    
    return templates.TemplateResponse("tree.html", {
        "request": request,
        "root_nodes": root_nodes,
        "current_user": current_user
    })

# 显示以指定节点为根的故事树
@router.get("/tree/node/{node_id}", response_class=HTMLResponse)
async def get_tree_node(request: Request, node_id: int, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    tree = get_story_tree(node_id)
    
    if not tree:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 渲染Markdown内容
    def render_content(node):
        node["content_html"] = markdown.markdown(node["content"])
        for child in node["children"]:
            render_content(child)
    
    root_node = tree[node_id]
    render_content(root_node)
    
    return templates.TemplateResponse("tree_node.html", {
        "request": request,
        "root_node": root_node,
        "current_user": current_user
    })

# 创建新节点
@router.post("/tree/node")
async def create_tree_node(request: Request, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    form_data = await request.form()
    title = form_data.get("title")
    option_title = form_data.get("option_title")
    content = form_data.get("content")
    parent_id = form_data.get("parent_id")
    
    if not title or not option_title or not content:
        raise HTTPException(status_code=400, detail="标题、选项标题和内容不能为空")
    
    # 生成新节点ID
    node_id = counters.get("story_tree_node", 1)
    counters["story_tree_node"] += 1
    
    # 创建新节点
    new_node = {
        "id": node_id,
        "title": title,
        "option_title": option_title,
        "content": content,
        "parent_id": int(parent_id) if parent_id else None,
        "author_id": current_user["id"],
        "created_at": datetime.now().isoformat()
    }
    
    # 添加到缓存
    enhanced_local_cache.add_item("story_tree_nodes", node_id, new_node)
    
    # 清除缓存的树结构，确保下次获取时重新构建
    if "cached_trees" in enhanced_local_cache.data:
        enhanced_local_cache.data["cached_trees"] = {}
    
    # 如果是内存存储模式，也添加到内存存储
    if "story_tree_nodes" in data_store:
        data_store["story_tree_nodes"].append(new_node)
    
    return {"id": node_id, "message": "节点创建成功"}

# 更新节点
@router.put("/tree/node/{node_id}")
async def update_tree_node(request: Request, node_id: int, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 检查节点是否存在
    node = enhanced_local_cache.get_item("story_tree_nodes", node_id)
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 检查权限
    if node["author_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权限修改此节点")
    
    form_data = await request.form()
    updates = {}
    
    if "title" in form_data:
        updates["title"] = form_data["title"]
    if "option_title" in form_data:
        updates["option_title"] = form_data["option_title"]
    if "content" in form_data:
        updates["content"] = form_data["content"]
    
    # 更新节点
    enhanced_local_cache.update_item("story_tree_nodes", node_id, updates)
    
    # 清除缓存的树结构，确保下次获取时重新构建
    if "cached_trees" in enhanced_local_cache.data:
        enhanced_local_cache.data["cached_trees"] = {}
    
    return {"id": node_id, "message": "节点更新成功"}

# 删除节点
@router.delete("/tree/node/{node_id}")
async def delete_tree_node(request: Request, node_id: int, db: Session = Depends(get_db)):
    current_user = await get_current_user(request, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="需要登录")
    
    # 检查节点是否存在
    node = enhanced_local_cache.get_item("story_tree_nodes", node_id)
    if not node:
        raise HTTPException(status_code=404, detail="节点不存在")
    
    # 检查权限
    if node["author_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权限删除此节点")
    
    # 递归删除子节点
    def delete_children(parent_id):
        for child_id, child_data in list(enhanced_local_cache.data.get("story_tree_nodes", {}).items()):
            if child_data.get("parent_id") == parent_id:
                delete_children(child_id)
                enhanced_local_cache.delete_item("story_tree_nodes", child_id)
    
    delete_children(node_id)
    enhanced_local_cache.delete_item("story_tree_nodes", node_id)
    
    # 清除缓存的树结构，确保下次获取时重新构建
    if "cached_trees" in enhanced_local_cache.data:
        enhanced_local_cache.data["cached_trees"] = {}
    
    return {"id": node_id, "message": "节点删除成功"}
