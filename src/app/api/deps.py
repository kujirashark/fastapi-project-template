"""FastAPI Depends 工厂。

提供:
- 数据库 session 注入
- DI 容器中各 Service 的注入(自动把请求级 session 注入到容器)
- 当前登录用户注入(JWT 鉴权)

统一使用 Annotated 风格声明依赖(FastAPI 官方推荐),可复用、无 B008 告警。
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.core.database import get_session_factory
from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.service.base.category import ICategoryService
from app.service.base.post import IPostService
from app.service.base.tag import ITagService
from app.service.base.user import IUserService

# ============ 基础依赖类型 ============

RequestDep = Annotated[Request, Depends()]
"""当前 Request 对象(用于从 app 上取 DI 容器)。"""


def _get_container(request: Request) -> Container:
    """从 FastAPI app 上取全局 Container 实例。"""
    return request.app.container


# ============ 数据库 Session ============

async def get_db_session() -> AsyncIterator[AsyncSession]:
    """每个请求一个新的 AsyncSession,自动 commit / rollback。"""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
"""请求级数据库 session(自动 commit / rollback)。"""


# ============ Service 注入 ============

def get_user_service(request: Request, session: SessionDep) -> IUserService:
    container = _get_container(request)
    with container.db_session.override(session):
        return container.user_service()


def get_post_service(request: Request, session: SessionDep) -> IPostService:
    container = _get_container(request)
    with container.db_session.override(session):
        return container.post_service()


def get_category_service(request: Request, session: SessionDep) -> ICategoryService:
    container = _get_container(request)
    with container.db_session.override(session):
        return container.category_service()


def get_tag_service(request: Request, session: SessionDep) -> ITagService:
    container = _get_container(request)
    with container.db_session.override(session):
        return container.tag_service()


# ============ 鉴权 ============

async def get_current_user(
    user_service: Annotated[IUserService, Depends(get_user_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """从 Authorization header 解析 JWT,返回当前用户。

    user_service 通过 FastAPI 依赖注入获取(嵌套 Depends 自动解析 session),
    不能手动调用 get_user_service(request),否则 session 参数会拿到
    Depends 标记对象而非真实 session。
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("缺少有效的 Authorization 头")
    token = authorization.split(" ", 1)[1]

    try:
        payload = decode_access_token(token)
    except Exception as exc:  # noqa: BLE001
        raise AuthenticationError(f"无效的令牌: {exc}") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("令牌缺少 sub 字段")

    return await user_service.get(int(user_id))


# ============ 常用依赖别名 ============

CurrentUser = Annotated[User, Depends(get_current_user)]
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
PostServiceDep = Annotated[IPostService, Depends(get_post_service)]
CategoryServiceDep = Annotated[ICategoryService, Depends(get_category_service)]
TagServiceDep = Annotated[ITagService, Depends(get_tag_service)]
