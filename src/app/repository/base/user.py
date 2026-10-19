"""User 仓储接口。"""

from typing import Protocol

from app.domain.entities.user import User
from app.repository.base.base import IBaseRepository


class IUserRepository(IBaseRepository[User, int], Protocol):
    """User 仓储协议:通用 CRUD + 用户特有的查询。"""

    async def get_by_username(self, username: str) -> User | None:
        """按用户名查询。"""
        ...

    async def get_by_email(self, email: str) -> User | None:
        """按邮箱查询。"""
        ...