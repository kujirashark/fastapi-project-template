"""Category 仓储 SQLAlchemy 实现。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.category import Category
from app.repository.base.category import ICategoryRepository
from app.repository.impl.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyCategoryRepository(
    SQLAlchemyBaseRepository[Category], ICategoryRepository
):
    """Category 仓储:基于 SQLAlchemy。"""

    model = Category

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> Category | None:
        stmt = select(Category).where(Category.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()