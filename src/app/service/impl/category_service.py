"""Category 业务服务实现。"""

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.entities.category import Category
from app.domain.schemas.category import CategoryCreate
from app.repository.base.category import ICategoryRepository


class CategoryService:
    """Category 业务服务。"""

    def __init__(self, category_repository: ICategoryRepository) -> None:
        self.category_repository = category_repository

    async def create(self, data: CategoryCreate) -> Category:
        if await self.category_repository.get_by_name(data.name):
            raise ConflictError(f"分类 {data.name} 已存在")

        category = Category(name=data.name, description=data.description)
        await self.category_repository.add(category)
        return category

    async def get(self, category_id: int) -> Category:
        category = await self.category_repository.get(category_id)
        if category is None:
            raise NotFoundError(f"分类 {category_id} 不存在")
        return category

    async def list(self, *, skip: int = 0, limit: int = 20) -> list[Category]:
        return await self.category_repository.list(skip=skip, limit=limit)

    async def delete(self, category_id: int) -> None:
        category = await self.get(category_id)
        await self.category_repository.delete(category)