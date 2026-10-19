"""依赖注入容器。

所有 Repository、Service 都注册到这里。
- `db_session` 声明为 `Dependency`,由 API 层在每个请求里通过 `override()` 注入
- API 层通过 `Depends(...)` 拿到 Service 实例,完全不直接 import 具体类
"""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.impl.category_repository import SQLAlchemyCategoryRepository
from app.repository.impl.post_repository import SQLAlchemyPostRepository
from app.repository.impl.tag_repository import SQLAlchemyTagRepository
from app.repository.impl.user_repository import SQLAlchemyUserRepository
from app.service.impl.category_service import CategoryService
from app.service.impl.post_service import PostService
from app.service.impl.tag_service import TagService
from app.service.impl.user_service import UserService


class Container(containers.DeclarativeContainer):
    """应用全局 DI 容器。

    调用示例(在 API 层):
        container = request.app.container
        container.db_session.override(session)
        user_service = container.user_service()
    """

    # 配置(从 pydantic Settings 加载)
    config = providers.Configuration()

    # 数据库 session:每个请求一个新 session,在使用时由 API 层 override 注入
    db_session: providers.Dependency[AsyncSession] = providers.Dependency(
        instance_of=AsyncSession
    )

    # ============ Repository 层 ============
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=db_session,
    )
    post_repository = providers.Factory(
        SQLAlchemyPostRepository,
        session=db_session,
    )
    category_repository = providers.Factory(
        SQLAlchemyCategoryRepository,
        session=db_session,
    )
    tag_repository = providers.Factory(
        SQLAlchemyTagRepository,
        session=db_session,
    )

    # ============ Service 层 ============
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )
    post_service = providers.Factory(
        PostService,
        post_repository=post_repository,
        user_repository=user_repository,
        category_repository=category_repository,
        tag_repository=tag_repository,
    )
    category_service = providers.Factory(
        CategoryService,
        category_repository=category_repository,
    )
    tag_service = providers.Factory(
        TagService,
        tag_repository=tag_repository,
    )