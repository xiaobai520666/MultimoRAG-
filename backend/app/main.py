"""FastAPI 应用入口"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router_v1 import router_v1
from app.core.config import get_settings
from app.core.exceptions import AppException


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="MultimoRAG",
        description="个人多模态 RAG 问答系统",
        version="0.1.0",
    )

    # CORS（前端开发用）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router_v1)

    # 异常处理
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=200,
            content={
                "code": exc.code,
                "data": None,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    # 日志
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return app


app = create_app()
