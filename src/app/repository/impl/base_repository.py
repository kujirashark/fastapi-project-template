"""通用仓储实现基类。

把 IBaseRepository 的通用方法抽出来,各实体仓储只需继承并指定 `model`。
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class SQLAlchemyBaseRepository(Generic[T]):
    """SQLAlchemy 通用仓储基类。"""

    model: type[T]  # 子类必须指定

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int | Any) -> T | None:
        return await self.session.get(self.model, id)

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> list[T]:
        stmt = select(self.model)
        for key, value in filters.items():
            if value is None:
                continue
            stmt = stmt.where(getattr(self.model, key) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if value is None:
                continue
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()

    async def flush(self) -> None:
        await self.session.flush()