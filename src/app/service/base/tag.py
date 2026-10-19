"""Tag 服务接口。"""

from typing import Protocol

from app.domain.entities.tag import Tag
from app.domain.schemas.tag import TagCreate
from app.service.base.base import IBaseService


class ITagService(IBaseService[Tag, int], Protocol):
    """Tag 服务协议。"""

    async def create(self, data: TagCreate) -> Tag:
        """创建标签(唯一名校验)。"""
        ...