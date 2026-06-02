"""健康检查"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/api/v1/health")
async def health_check():
    return {"code": 0, "data": {"status": "ok"}, "message": "ok"}
