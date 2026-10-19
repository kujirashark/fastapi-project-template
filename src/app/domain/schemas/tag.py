"""Tag 相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    """Tag 公共字段。"""

    name: str = Field(min_length=1, max_length=50)


class TagCreate(TagBase):
    """创建标签。"""

    pass


class TagOut(TagBase):
    """标签响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime