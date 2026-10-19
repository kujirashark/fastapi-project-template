"""FastAPI 应用入口。

负责:
- 创建 FastAPI 实例
- 装配 DI 容器
- 注册路由
- 注册全局异常处理
- 配置启动/关闭钩子
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.v1.router import api_router
from app.containers import Container
from app.core.config import get_settings
from app.core.database import dispose_engine, init_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期:启动时初始化引擎,关闭时释放连接池。"""
    settings = get_settings()
    # 启动
    init_engine(settings)
    yield
    # 关闭
    await dispose_engine()


def create_app() -> FastAPI:
    """工厂函数:创建并配置 FastAPI 实例。"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        debug=settings.app_debug,
        lifespan=lifespan,
    )

    # 装配 DI 容器
    container = Container()
    container.config.from_pydantic(settings)
    app.container = container  # type: ignore[attr-defined]

    # 注册全局异常处理
    register_exception_handlers(app)

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    # 健康检查
    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()