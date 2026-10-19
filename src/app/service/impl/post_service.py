"""Post 业务服务实现。"""

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.domain.entities.post import Post
from app.domain.entities.tag import Tag
from app.domain.schemas.common import PageInfo, PaginatedResponse
from app.domain.schemas.post import PostCreate, PostListItem, PostUpdate
from app.repository.base.category import ICategoryRepository
from app.repository.base.post import IPostRepository
from app.repository.base.tag import ITagRepository
from app.repository.base.user import IUserRepository


class PostService:
    """Post 业务服务:文章的领域规则集中地。"""

    def __init__(
        self,
        post_repository: IPostRepository,
        user_repository: IUserRepository,
        category_repository: ICategoryRepository,
        tag_repository: ITagRepository,
    ) -> None:
        self.post_repository = post_repository
        self.user_repository = user_repository
        self.category_repository = category_repository
        self.tag_repository = tag_repository

    async def create(self, data: PostCreate, author_id: int) -> Post:
        # 校验作者
        author = await self.user_repository.get(author_id)
        if author is None:
            raise NotFoundError(f"作者 {author_id} 不存在")

        # 校验分类
        if data.category_id is not None:
            category = await self.category_repository.get(data.category_id)
            if category is None:
                raise NotFoundError(f"分类 {data.category_id} 不存在")

        # 校验标签
        tags: list[Tag] = []
        if data.tag_ids:
            tags = await self.tag_repository.get_many_by_ids(data.tag_ids)
            found_ids = {t.id for t in tags}
            missing = set(data.tag_ids) - found_ids
            if missing:
                raise ValidationError(
                    f"以下标签不存在: {sorted(missing)}",
                    details={"missing_tag_ids": sorted(missing)},
                )

        post = Post(
            title=data.title,
            summary=data.summary,
            content=data.content,
            author_id=author_id,
            category_id=data.category_id,
            tags=tags,
        )
        await self.post_repository.add(post)
        return post

    async def get(self, post_id: int) -> Post:
        post = await self.post_repository.get(post_id)
        if post is None:
            raise NotFoundError(f"文章 {post_id} 不存在")
        return post

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        author_id: int | None = None,
        category_id: int | None = None,
        tag_id: int | None = None,
    ) -> PaginatedResponse[PostListItem]:
        posts, total = await self.post_repository.list_paginated(
            page=page,
            page_size=page_size,
            keyword=keyword,
            author_id=author_id,
            category_id=category_id,
            tag_id=tag_id,
        )
        return PaginatedResponse[PostListItem](
            items=[PostListItem.model_validate(p) for p in posts],
            page_info=PageInfo(page=page, page_size=page_size, total=total),
        )

    async def update(
        self,
        post_id: int,
        data: PostUpdate,
        current_user_id: int,
    ) -> Post:
        post = await self.get(post_id)

        # 权限校验:只有作者本人能改
        if post.author_id != current_user_id:
            raise PermissionDeniedError("只能修改自己的文章")

        # 更新字段
        if data.title is not None:
            post.title = data.title
        if data.summary is not None:
            post.summary = data.summary
        if data.content is not None:
            post.content = data.content
        if data.category_id is not None:
            if data.category_id == 0:
                post.category_id = None
            else:
                category = await self.category_repository.get(data.category_id)
                if category is None:
                    raise NotFoundError(f"分类 {data.category_id} 不存在")
                post.category_id = data.category_id

        if data.tag_ids is not None:
            tags = await self.tag_repository.get_many_by_ids(data.tag_ids)
            found_ids = {t.id for t in tags}
            missing = set(data.tag_ids) - found_ids
            if missing:
                raise ValidationError(
                    f"以下标签不存在: {sorted(missing)}",
                    details={"missing_tag_ids": sorted(missing)},
                )
            post.tags = tags

        await self.post_repository.flush()
        return post

    async def delete(self, post_id: int, current_user_id: int) -> None:
        post = await self.get(post_id)
        if post.author_id != current_user_id:
            raise PermissionDeniedError("只能删除自己的文章")
        await self.post_repository.delete(post)