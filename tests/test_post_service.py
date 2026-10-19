"""PostService 单元测试示例。"""

import pytest

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.domain.schemas.category import CategoryCreate
from app.domain.schemas.post import PostCreate, PostUpdate
from app.domain.schemas.tag import TagCreate
from app.domain.schemas.user import UserCreate
from app.repository.impl.category_repository import SQLAlchemyCategoryRepository
from app.repository.impl.post_repository import SQLAlchemyPostRepository
from app.repository.impl.tag_repository import SQLAlchemyTagRepository
from app.repository.impl.user_repository import SQLAlchemyUserRepository
from app.service.impl.category_service import CategoryService
from app.service.impl.post_service import PostService
from app.service.impl.tag_service import TagService
from app.service.impl.user_service import UserService


@pytest.fixture
async def services(
    user_repo: SQLAlchemyUserRepository,
    post_repo: SQLAlchemyPostRepository,
    category_repo: SQLAlchemyCategoryRepository,
    tag_repo: SQLAlchemyTagRepository,
):
    """组装所有 service(展示 DI 装配关系)。"""
    return {
        "user": UserService(user_repository=user_repo),
        "post": PostService(
            post_repository=post_repo,
            user_repository=user_repo,
            category_repository=category_repo,
            tag_repository=tag_repo,
        ),
        "category": CategoryService(category_repository=category_repo),
        "tag": TagService(tag_repository=tag_repo),
    }


@pytest.mark.asyncio
async def test_create_post_full_flow(services):
    # 准备数据
    user = await services["user"].register(
        UserCreate(username="bob", email="bob@example.com", password="secret123")
    )
    category = await services["category"].create(CategoryCreate(name="技术"))
    tag = await services["tag"].create(TagCreate(name="Python"))

    # 创建文章
    post = await services["post"].create(
        PostCreate(
            title="Hello",
            content="Content here",
            summary="摘要",
            category_id=category.id,
            tag_ids=[tag.id],
        ),
        author_id=user.id,
    )

    assert post.id is not None
    assert post.author_id == user.id
    assert post.category_id == category.id
    assert tag in post.tags


@pytest.mark.asyncio
async def test_update_post_requires_author(services):
    author = await services["user"].register(
        UserCreate(username="alice", email="a@example.com", password="secret123")
    )
    other = await services["user"].register(
        UserCreate(username="bob", email="b@example.com", password="secret123")
    )
    post = await services["post"].create(
        PostCreate(title="Original", content="x"),
        author_id=author.id,
    )

    # 别人改应该被拒绝
    with pytest.raises(PermissionDeniedError):
        await services["post"].update(
            post.id,
            data=PostUpdate(title="Hijacked"),
            current_user_id=other.id,
        )


@pytest.mark.asyncio
async def test_list_paginated(services):
    user = await services["user"].register(
        UserCreate(username="alice", email="a@example.com", password="secret123")
    )
    for i in range(3):
        await services["post"].create(
            PostCreate(title=f"Post {i}", content="x"),
            author_id=user.id,
        )

    page = await services["post"].list_paginated(page=1, page_size=2)
    assert len(page.items) == 2
    assert page.page_info.total == 3


@pytest.mark.asyncio
async def test_get_post_not_found(services):
    with pytest.raises(NotFoundError):
        await services["post"].get(9999)