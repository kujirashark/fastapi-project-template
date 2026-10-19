"""Category 服务接口。"""

from typing import Protocol

from app.domain.entities.category import Category
from app.domain.schemas.category import CategoryCreate
from app.service.base.base import IBaseService


class ICategoryService(IBaseService[Category, int], Protocol):
    """Category 服务协议。"""

    async def create(self, data: CategoryCreate) -> Category:
        """创建分类(唯一名校验)。"""
        ...