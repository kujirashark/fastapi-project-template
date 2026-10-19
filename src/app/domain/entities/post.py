"""Post 实体:文章。"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import Base, TimestampMixin
from app.domain.entities.tag import post_tags

if TYPE_CHECKING:
    from app.domain.entities.category import Category
    from app.domain.entities.tag import Tag
    from app.domain.entities.user import User


class Post(Base, TimestampMixin):
    """文章表:作者 + 分类 + 标签。"""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 作者(必填)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author: Mapped["User"] = relationship("User", back_populates="posts", lazy="joined")

    # 分类(可选)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="posts", lazy="joined"
    )

    # 标签(多对多)
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} title={self.title!r}>"