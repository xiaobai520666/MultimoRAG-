"""统一路由注册"""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.knowledge import router as knowledge_router
from app.api.chat import router as chat_router
from app.api.ingestion import router as ingestion_router
from app.api.retrieval import router as retrieval_router
from app.api.agent import router as agent_router

router_v1 = APIRouter()

# 注册所有路由
router_v1.include_router(health_router)
router_v1.include_router(knowledge_router)
router_v1.include_router(chat_router)
router_v1.include_router(ingestion_router)
router_v1.include_router(retrieval_router)
router_v1.include_router(agent_router)
