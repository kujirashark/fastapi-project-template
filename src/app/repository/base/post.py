"""Post 仓储接口。"""

from typing import Protocol

from app.domain.entities.post import Post
from app.repository.base.base import IBaseRepository


class IPostRepository(IBaseRepository[Post, int], Protocol):
    """Post 仓储协议:通用 CRUD + 文章特有的查询。"""

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        author_id: int | None = None,
        category_id: int | None = None,
        tag_id: int | None = None,
    ) -> tuple[list[Post], int]:
        """分页查询文章,支持搜索和筛选。

        Returns:
            (items, total)
        """
        ...