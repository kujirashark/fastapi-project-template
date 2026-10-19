"""通用仓储接口。

所有实体仓储都继承本接口,获得通用的 CRUD 能力,然后再扩展自己的方法。
"""

from typing import Any, Generic, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=Any)
ID = TypeVar("ID", bound=Any)


class IBaseRepository(Protocol, Generic[T, ID]):
    """通用仓储协议:任何实体仓储都至少有这些方法。"""

    session: AsyncSession

    async def get(self, id: ID) -> T | None:
        """按主键查询,找不到返回 None。"""
        ...

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> list[T]:
        """分页查询。"""
        ...

    async def count(self, **filters: Any) -> int:
        """统计数量。"""
        ...

    async def add(self, entity: T) -> T:
        """新增(不提交事务,由调用方控制 commit)。"""
        ...

    async def delete(self, entity: T) -> None:
        """删除(不提交事务)。"""
        ...

    async def flush(self) -> None:
        """flush 当前事务的更改,但不 commit。"""
        ...