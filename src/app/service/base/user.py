"""User 服务接口。"""

from typing import Protocol

from app.domain.entities.user import User
from app.domain.schemas.user import LoginRequest, TokenResponse, UserCreate, UserUpdate
from app.service.base.base import IBaseService


class IUserService(IBaseService[User, int], Protocol):
    """User 服务协议。"""

    async def register(self, data: UserCreate) -> User:
        """注册新用户(用户名/邮箱唯一性校验+密码哈希)。"""
        ...

    async def login(self, data: LoginRequest) -> TokenResponse:
        """登录校验,返回 JWT。"""
        ...

    async def update(self, user_id: int, data: UserUpdate) -> User:
        """更新用户资料。"""
        ...

    async def get_by_username(self, username: str) -> User | None:
        """按用户名查询(可选实现)。"""
        ...