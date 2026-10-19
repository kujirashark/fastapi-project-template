"""通用业务服务接口。"""

from typing import Generic, Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class IBaseService(Protocol, Generic[T, ID]):
    """通用业务服务协议。"""

    async def get(self, id: ID) -> T:
        """按 id 获取(找不到抛 NotFoundError)。"""
        ...

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[T]:
        """列表查询。"""
        ...

    async def delete(self, id: ID) -> None:
        """删除。"""
        ...