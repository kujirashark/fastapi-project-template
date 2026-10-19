"""测试公共 fixture。

- 使用 SQLite 内存数据库 + aiosqlite(避免依赖真实 MySQL)
- 每个测试一个全新 session,事务隔离
"""

from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.domain.entities import category, post, tag, user  # noqa: F401 触发 metadata
from app.domain.entities.base import Base

# ============ 数据库 ============

@pytest_asyncio.fixture
async def db_engine() -> AsyncIterator[Any]:
    """每个测试一个新的内存数据库。"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: Any) -> AsyncIterator[AsyncSession]:
    """每个测试一个 session。"""
    factory = async_sessionmaker(
        bind=db_engine, expire_on_commit=False, autoflush=False
    )
    async with factory() as session:
        yield session


# ============ 设置 ============

@pytest.fixture
def settings() -> Settings:
    """测试用配置(可覆盖默认值)。"""
    return Settings(secret_key="test-secret-key-for-jwt")


# ============ Repository Fixtures(可选,实际测试里直接构造) ============

@pytest_asyncio.fixture
async def user_repo(db_session: AsyncSession):
    from app.repository.impl.user_repository import SQLAlchemyUserRepository

    return SQLAlchemyUserRepository(db_session)


@pytest_asyncio.fixture
async def post_repo(db_session: AsyncSession):
    from app.repository.impl.post_repository import SQLAlchemyPostRepository

    return SQLAlchemyPostRepository(db_session)


@pytest_asyncio.fixture
async def category_repo(db_session: AsyncSession):
    from app.repository.impl.category_repository import SQLAlchemyCategoryRepository

    return SQLAlchemyCategoryRepository(db_session)


@pytest_asyncio.fixture
async def tag_repo(db_session: AsyncSession):
    from app.repository.impl.tag_repository import SQLAlchemyTagRepository

    return SQLAlchemyTagRepository(db_session)