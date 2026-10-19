"""Category 实体:文章分类。"""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.entities.post import Post


class Category(Base, TimestampMixin):
    """分类表:一个分类下有多篇文章。"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="category",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"