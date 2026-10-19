"""Pydantic 数据传输对象(DTO):输入/输出模型。"""

from app.domain.schemas.category import CategoryCreate, CategoryOut
from app.domain.schemas.common import PageInfo, PaginatedResponse
from app.domain.schemas.post import PostCreate, PostListItem, PostOut, PostUpdate
from app.domain.schemas.tag import TagCreate, TagOut
from app.domain.schemas.user import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserOut,
    UserUpdate,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "LoginRequest",
    "TokenResponse",
    "CategoryCreate",
    "CategoryOut",
    "TagCreate",
    "TagOut",
    "PostCreate",
    "PostUpdate",
    "PostOut",
    "PostListItem",
    "PageInfo",
    "PaginatedResponse",
]