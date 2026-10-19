"""Post 相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.schemas.category import CategoryOut
from app.domain.schemas.tag import TagOut
from app.domain.schemas.user import UserOut


class PostBase(BaseModel):
    """Post 公共字段。"""

    title: str = Field(min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str = Field(min_length=1)
    category_id: int | None = None
    tag_ids: list[int] = Field(default_factory=list)


class PostCreate(PostBase):
    """创建文章。"""

    pass


class PostUpdate(BaseModel):
    """更新文章(全部可选)。"""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=1)
    category_id: int | None = None
    tag_ids: list[int] | None = None


class PostOut(PostBase):
    """文章详情响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    author: UserOut
    category: CategoryOut | None = None
    tags: list[TagOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PostListItem(BaseModel):
    """文章列表项(精简字段)。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None
    author_id: int
    category_id: int | None
    created_at: datetime