"""Post 仓储 SQLAlchemy 实现。"""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.post import Post
from app.repository.base.post import IPostRepository
from app.repository.impl.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyPostRepository(SQLAlchemyBaseRepository[Post], IPostRepository):
    """Post 仓储:基于 SQLAlchemy。"""

    model = Post

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        author_id: int | None = None,
        category_id: int | None = None,
        tag_id: int | None = None,
    ) -> tuple[list[Post], int]:
        """分页查询,支持按关键词/作者/分类/标签筛选。"""
        # 基础查询
        stmt = select(Post)
        count_stmt = select(func.count()).select_from(Post)

        # 拼接过滤条件
        conditions = []
        if keyword:
            like = f"%{keyword}%"
            conditions.append(or_(Post.title.like(like), Post.summary.like(like)))
        if author_id is not None:
            conditions.append(Post.author_id == author_id)
        if category_id is not None:
            conditions.append(Post.category_id == category_id)
        if tag_id is not None:
            stmt = stmt.join(Post.tags).where(Post.tags.any(id=tag_id))
            # count 需要 distinct 去重
            count_stmt = (
                select(func.count(func.distinct(Post.id)))
                .select_from(Post)
                .join(Post.tags)
                .where(Post.tags.any(id=tag_id))
            )

        for cond in conditions:
            stmt = stmt.where(cond)
            count_stmt = count_stmt.where(cond)

        # 排序 + 分页
        stmt = stmt.order_by(Post.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size)

        items_result = await self.session.execute(stmt)
        items = list(items_result.unique().scalars().all())

        total_result = await self.session.execute(count_stmt)
        total = int(total_result.scalar_one())

        return items, total