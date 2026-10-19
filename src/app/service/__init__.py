"""业务逻辑层:领域规则集中地,接口与实现分离。"""

from app.service.base.base import IBaseService
from app.service.base.category import ICategoryService
from app.service.base.post import IPostService
from app.service.base.tag import ITagService
from app.service.base.user import IUserService

__all__ = [
    "IBaseService",
    "IUserService",
    "ICategoryService",
    "ITagService",
    "IPostService",
]