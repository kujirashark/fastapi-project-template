"""User 仓储 SQLAlchemy 实现。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.repository.base.user import IUserRepository
from app.repository.impl.base_repository import SQLAlchemyBaseRepository


class SQLAlchemyUserRepository(SQLAlchemyBaseRepository[User], IUserRepository):
    """User 仓储:基于 SQLAlchemy。"""

    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()