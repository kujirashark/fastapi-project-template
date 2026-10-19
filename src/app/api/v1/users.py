"""用户相关路由。"""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, UserServiceDep
from app.domain.schemas.user import UserOut, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserOut, summary="获取当前登录用户")
async def get_me(current_user: CurrentUser) -> UserOut:
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut, summary="更新当前用户资料")
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserOut:
    user = await user_service.update(current_user.id, data)
    return UserOut.model_validate(user)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="注销当前用户",
)
async def delete_me(
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> None:
    await user_service.delete(current_user.id)