"""异步 SQLAlchemy 引擎和 Session 管理。

- 全局只有一个 engine(应用启动时初始化)
- 每个请求一个 session(在 api/deps.py 里创建)
- 提供 init/dispose 钩子配合 FastAPI lifespan
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings

# 模块级单例
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(settings: Settings) -> None:
    """初始化全局引擎(在 FastAPI lifespan 启动时调用)。"""
    global _engine, _session_factory
    if _engine is not None:
        return

    _engine = create_async_engine(
        settings.database_url,
        echo=settings.app_debug,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,
        max_overflow=20,
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def dispose_engine() -> None:
    """释放连接池(在 FastAPI lifespan 关闭时调用)。"""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取 session 工厂。"""
    if _session_factory is None:
        raise RuntimeError(
            "数据库未初始化,请确认 FastAPI lifespan 已启动,或在测试中手动调用 init_engine()"
        )
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """异步 session 生成器,FastAPI Depends 用。

    用法:
        @router.get(...)
        async def handler(session: AsyncSession = Depends(get_session)):
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        yield session