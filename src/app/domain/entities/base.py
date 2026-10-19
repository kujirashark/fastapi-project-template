"""ORM 基类 + 公共字段。"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有 ORM 实体的基类。"""

    pass


class TimestampMixin:
    """时间戳混入类:created_at + updated_at。

    eager_defaults=True:flush 时立即回读服务端生成的默认值/更新值,
    避免之后同步访问 updated_at 触发懒加载(MissingGreenlet 错误)。
    """

    __mapper_args__ = {"eager_defaults": True}

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )