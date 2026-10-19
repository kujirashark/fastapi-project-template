"""通用分页响应模型。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageInfo(BaseModel):
    """分页信息。"""

    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    total: int = Field(default=0, ge=0, description="总记录数")


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应。"""

    items: list[T] = Field(default_factory=list, description="数据列表")
    page_info: PageInfo = Field(description="分页信息")