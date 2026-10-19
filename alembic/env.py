"""Alembic 迁移环境配置。

- 使用同步驱动(pymysql),因为 Alembic 本身是同步工具
- target_metadata 指向 SQLAlchemy DeclarativeBase
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 导入项目配置和模型
from app.core.config import get_settings
from app.domain.entities.base import Base
# 显式 import 所有模型,让 Base.metadata 能发现它们
from app.domain.entities import (  # noqa: F401
    user,
    category,
    tag,
    post,
)

config = context.config

# 用 Settings 里的数据库 URL 覆盖 alembic.ini 中的配置
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """离线模式:生成 SQL 脚本但不执行。"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式:直接连接数据库执行迁移。"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()