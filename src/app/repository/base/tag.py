"""Tag 仓储接口。"""

from typing import Protocol

from app.domain.entities.tag import Tag
from app.repository.base.base import IBaseRepository


class ITagRepository(IBaseRepository[Tag, int], Protocol):
    """Tag 仓储协议。"""

    async def get_by_name(self, name: str) -> Tag | None:
        """按名称查询。"""
        ...

    async def get_many_by_ids(self, ids: list[int]) -> list[Tag]:
        """按 id 列表批量查询。"""
        ...