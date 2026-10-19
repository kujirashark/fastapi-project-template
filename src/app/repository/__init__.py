"""仓储层:封装所有数据库操作,接口与实现分离。"""

from app.repository.base.base import IBaseRepository
from app.repository.base.category import ICategoryRepository
from app.repository.base.post import IPostRepository
from app.repository.base.tag import ITagRepository
from app.repository.base.user import IUserRepository

__all__ = [
    "IBaseRepository",
    "IUserRepository",
    "ICategoryRepository",
    "ITagRepository",
    "IPostRepository",
]