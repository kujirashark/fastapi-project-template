"""Tag 业务服务实现。"""

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.entities.tag import Tag
from app.domain.schemas.tag import TagCreate
from app.repository.base.tag import ITagRepository


class TagService:
    """Tag 业务服务。"""

    def __init__(self, tag_repository: ITagRepository) -> None:
        self.tag_repository = tag_repository

    async def create(self, data: TagCreate) -> Tag:
        if await self.tag_repository.get_by_name(data.name):
            raise ConflictError(f"标签 {data.name} 已存在")

        tag = Tag(name=data.name)
        await self.tag_repository.add(tag)
        return tag

    async def get(self, tag_id: int) -> Tag:
        tag = await self.tag_repository.get(tag_id)
        if tag is None:
            raise NotFoundError(f"标签 {tag_id} 不存在")
        return tag

    async def list(self, *, skip: int = 0, limit: int = 20) -> list[Tag]:
        return await self.tag_repository.list(skip=skip, limit=limit)

    async def delete(self, tag_id: int) -> None:
        tag = await self.get(tag_id)
        await self.tag_repository.delete(tag)