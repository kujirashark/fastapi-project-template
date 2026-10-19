"""文章路由:增删改查 + 分页搜索。"""

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, PostServiceDep
from app.domain.schemas.common import PaginatedResponse
from app.domain.schemas.post import PostCreate, PostListItem, PostOut, PostUpdate

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[PostListItem],
    summary="文章列表(分页+搜索)",
)
async def list_posts(
    post_service: PostServiceDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, description="标题/摘要关键词"),
    author_id: int | None = Query(default=None),
    category_id: int | None = Query(default=None),
    tag_id: int | None = Query(default=None),
) -> PaginatedResponse[PostListItem]:
    return await post_service.list_paginated(
        page=page,
        page_size=page_size,
        keyword=keyword,
        author_id=author_id,
        category_id=category_id,
        tag_id=tag_id,
    )


@router.post(
    "",
    response_model=PostOut,
    status_code=status.HTTP_201_CREATED,
    summary="创建文章",
)
async def create_post(
    data: PostCreate,
    current_user: CurrentUser,
    post_service: PostServiceDep,
) -> PostOut:
    post = await post_service.create(data, author_id=current_user.id)
    return PostOut.model_validate(post)


@router.get("/{post_id}", response_model=PostOut, summary="文章详情")
async def get_post(
    post_id: int,
    post_service: PostServiceDep,
) -> PostOut:
    post = await post_service.get(post_id)
    return PostOut.model_validate(post)


@router.put("/{post_id}", response_model=PostOut, summary="更新文章(作者本人)")
async def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: CurrentUser,
    post_service: PostServiceDep,
) -> PostOut:
    post = await post_service.update(post_id, data, current_user_id=current_user.id)
    return PostOut.model_validate(post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除文章(作者本人)",
)
async def delete_post(
    post_id: int,
    current_user: CurrentUser,
    post_service: PostServiceDep,
) -> None:
    await post_service.delete(post_id, current_user_id=current_user.id)