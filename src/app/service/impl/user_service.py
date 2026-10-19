"""User 业务服务实现。"""

from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
)
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.domain.entities.user import User
from app.domain.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserUpdate,
)
from app.repository.base.user import IUserRepository


class UserService:
    """User 业务服务。

    依赖通过构造函数注入(DI 容器负责装配),不直接 import 具体实现类。
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        self.user_repository = user_repository

    async def register(self, data: UserCreate) -> User:
        """注册:校验唯一性 + 哈希密码。"""
        # 校验用户名唯一
        if await self.user_repository.get_by_username(data.username):
            raise ConflictError(f"用户名 {data.username} 已被占用")

        # 校验邮箱唯一
        if await self.user_repository.get_by_email(data.email):
            raise ConflictError(f"邮箱 {data.email} 已被注册")

        user = User(
            username=data.username,
            email=data.email,
            password_hash=get_password_hash(data.password),
        )
        await self.user_repository.add(user)
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        """登录:支持用户名或邮箱登录。"""
        # 优先按用户名查,再按邮箱查
        user = await self.user_repository.get_by_username(data.username)
        if user is None and "@" in data.username:
            user = await self.user_repository.get_by_email(data.username)

        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthenticationError("用户名或密码错误")

        if not user.is_active:
            raise AuthenticationError("用户已被禁用")

        settings = get_settings()
        token = create_access_token(
            subject=user.id,
            extra_claims={"username": user.username},
        )
        return TokenResponse(
            access_token=token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def get(self, user_id: int) -> User:
        user = await self.user_repository.get(user_id)
        if user is None:
            raise NotFoundError(f"用户 {user_id} 不存在")
        return user

    async def get_by_username(self, username: str) -> User | None:
        return await self.user_repository.get_by_username(username)

    async def list(self, *, skip: int = 0, limit: int = 20) -> list[User]:
        return await self.user_repository.list(skip=skip, limit=limit)

    async def update(self, user_id: int, data: UserUpdate) -> User:
        user = await self.get(user_id)

        if data.username and data.username != user.username:
            if await self.user_repository.get_by_username(data.username):
                raise ConflictError(f"用户名 {data.username} 已被占用")
            user.username = data.username

        if data.email and data.email != user.email:
            if await self.user_repository.get_by_email(data.email):
                raise ConflictError(f"邮箱 {data.email} 已被注册")
            user.email = data.email

        if data.password:
            user.password_hash = get_password_hash(data.password)

        await self.user_repository.flush()
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get(user_id)
        await self.user_repository.delete(user)