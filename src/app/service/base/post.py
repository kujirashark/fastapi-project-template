"""Post 服务接口。"""

from typing import Protocol

from app.domain.entities.post import Post
from app.domain.schemas.common import PaginatedResponse
from app.domain.schemas.post import PostCreate, PostListItem, PostUpdate
from app.service.base.base import IBaseService


class IPostService(IBaseService[Post, int], Protocol):
    """Post 服务协议。"""

    async def create(self, data: PostCreate, author_id: int) -> Post:
        """创建文章(校验作者/分类/标签存在)。"""
        ...

    async def update(self, post_id: int, data: PostUpdate, current_user_id: int) -> Post:
        """更新文章(校验当前用户是作者本人)。"""
        ...

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        author_id: int | None = None,
        category_id: int | None = None,
        tag_id: int | None = None,
    ) -> PaginatedResponse[PostListItem]:
        """分页查询文章。"""
        ...