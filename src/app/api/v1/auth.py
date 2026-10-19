"""认证相关路由:注册、登录。"""

from fastapi import APIRouter, status

from app.api.deps import UserServiceDep
from app.domain.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserOut,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
async def register(
    data: UserCreate,
    user_service: UserServiceDep,
) -> UserOut:
    user = await user_service.register(data)
    return UserOut.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录(用户名或邮箱)",
)
async def login(
    data: LoginRequest,
    user_service: UserServiceDep,
) -> TokenResponse:
    return await user_service.login(data)