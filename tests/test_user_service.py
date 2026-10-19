"""UserService 单元测试示例。"""

import pytest

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.domain.schemas.user import LoginRequest, UserCreate
from app.repository.impl.user_repository import SQLAlchemyUserRepository
from app.service.impl.user_service import UserService


@pytest.mark.asyncio
async def test_register_success(user_repo: SQLAlchemyUserRepository):
    service = UserService(user_repository=user_repo)
    user = await service.register(
        UserCreate(username="alice", email="alice@example.com", password="secret123")
    )

    assert user.id is not None
    assert user.username == "alice"
    assert user.password_hash != "secret123"  # 已哈希
    assert user.is_active is True


@pytest.mark.asyncio
async def test_register_duplicate_username(user_repo: SQLAlchemyUserRepository):
    service = UserService(user_repository=user_repo)
    await service.register(
        UserCreate(username="alice", email="a@example.com", password="secret123")
    )
    with pytest.raises(ConflictError):
        await service.register(
            UserCreate(username="alice", email="b@example.com", password="secret123")
        )


@pytest.mark.asyncio
async def test_login_success(user_repo: SQLAlchemyUserRepository):
    service = UserService(user_repository=user_repo)
    await service.register(
        UserCreate(username="alice", email="alice@example.com", password="secret123")
    )

    token = await service.login(LoginRequest(username="alice", password="secret123"))
    assert token.access_token
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(user_repo: SQLAlchemyUserRepository):
    service = UserService(user_repository=user_repo)
    await service.register(
        UserCreate(username="alice", email="alice@example.com", password="secret123")
    )

    with pytest.raises(AuthenticationError):
        await service.login(LoginRequest(username="alice", password="wrong"))


@pytest.mark.asyncio
async def test_get_not_found(user_repo: SQLAlchemyUserRepository):
    service = UserService(user_repository=user_repo)
    with pytest.raises(NotFoundError):
        await service.get(9999)