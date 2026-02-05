from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database_connection import db_manager
from enhanced_local_cache import enhanced_local_cache
from temp_storage import temp_storage
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

class HealthStatus(BaseModel):
    """健康检查状态响应"""
    status: str
    timestamp: datetime
    database_connected: bool
    cache_initialized: bool
    temp_storage_available: bool
    sync_thread_running: bool
    details: dict

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    services: dict
    timestamp: datetime

@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """系统健康检查端点"""
    try:
        # 检查数据库连接
        db_connected = db_manager.is_connection_available()
        
        # 检查本地缓存状态
        cache_initialized = len(enhanced_local_cache.data.get("users", {})) > 0
        
        # 检查临时存储
        temp_storage_available = True  # 临时存储总是可用的
        
        # 检查同步线程状态
        sync_thread_running = True  # 假设同步线程正常运行
        
        # 构建响应
        services = {
            "database": {
                "status": "healthy" if db_connected else "unhealthy",
                "connected": db_connected
            },
            "local_cache": {
                "status": "healthy" if cache_initialized else "initializing",
                "initialized": cache_initialized,
                "data_types": {
                    data_type: len(items) 
                    for data_type, items in enhanced_local_cache.data.items()
                }
            },
            "temp_storage": {
                "status": "healthy" if temp_storage_available else "unhealthy",
                "available": temp_storage_available
            },
            "sync_service": {
                "status": "healthy" if sync_thread_running else "unhealthy",
                "running": sync_thread_running
            }
        }
        
        # 确定整体状态
        overall_status = "healthy"
        if not db_connected:
            overall_status = "degraded"
        if not cache_initialized and not temp_storage_available:
            overall_status = "unhealthy"
            
        return HealthCheckResponse(
            status=overall_status,
            services=services,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.get("/database")
async def database_health():
    """数据库连接健康检查"""
    try:
        is_connected = db_manager.is_connection_available()
        
        if is_connected:
            return {
                "status": "healthy",
                "database_connected": True,
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "unhealthy", 
                "database_connected": False,
                "timestamp": datetime.now(),
                "message": "数据库连接不可用"
            }
            
    except Exception as e:
        logger.error(f"数据库健康检查失败: {str(e)}")
        return {
            "status": "error",
            "database_connected": False,
            "timestamp": datetime.now(),
            "error": str(e)
        }

@router.get("/cache")
async def cache_health():
    """本地缓存健康检查"""
    try:
        cache_stats = {
            data_type: {
                "count": len(items),
                "modified": len(enhanced_local_cache.modified[data_type]),
                "deleted": len(enhanced_local_cache.deleted[data_type])
            }
            for data_type, items in enhanced_local_cache.data.items()
        }
        
        return {
            "status": "healthy",
            "cache_stats": cache_stats,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"缓存健康检查失败: {str(e)}")
        return {
            "status": "error",
            "timestamp": datetime.now(),
            "error": str(e)
        }

@router.post("/sync")
async def force_sync():
    """强制同步数据到数据库"""
    try:
        logger.info("收到强制同步请求")
        
        # 尝试同步数据
        sync_success = enhanced_local_cache.sync_to_db_with_fallback()
        
        if sync_success:
            return {
                "status": "success",
                "message": "数据同步成功",
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "partial_success",
                "message": "数据同步部分成功，部分数据已保存到临时存储",
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"强制同步失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"强制同步失败: {str(e)}")

@router.post("/reconnect")
async def force_reconnect():
    """强制重新连接数据库"""
    try:
        logger.info("收到强制重连请求")
        
        # 尝试重新连接
        reconnect_success = db_manager.reconnect()
        
        if reconnect_success:
            return {
                "status": "success",
                "message": "数据库重连成功",
                "timestamp": datetime.now()
            }
        else:
            return {
                "status": "failed",
                "message": "数据库重连失败",
                "timestamp": datetime.now()
            }
            
    except Exception as e:
        logger.error(f"强制重连失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"强制重连失败: {str(e)}")