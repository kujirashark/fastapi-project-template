"""Category 相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    """Category 公共字段。"""

    name: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=255)


class CategoryCreate(CategoryBase):
    """创建分类。"""

    pass


class CategoryOut(CategoryBase):
    """分类响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime