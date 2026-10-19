"""Category 仓储接口。"""

from typing import Protocol

from app.domain.entities.category import Category
from app.repository.base.base import IBaseRepository


class ICategoryRepository(IBaseRepository[Category, int], Protocol):
    """Category 仓储协议。"""

    async def get_by_name(self, name: str) -> Category | None:
        """按名称查询。"""
        ...