"""Tag 仓储 SQLAlchemy 实现。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tag import Tag
from app.repository.base.tag import ITagRepository
from app.repository.impl.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyTagRepository(SQLAlchemyBaseRepository[Tag], ITagRepository):
    """Tag 仓储:基于 SQLAlchemy。"""

    model = Tag

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> Tag | None:
        stmt = select(Tag).where(Tag.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many_by_ids(self, ids: list[int]) -> list[Tag]:
        if not ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())