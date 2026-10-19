"""应用配置。

使用 pydantic-settings 从环境变量(和 .env 文件)加载配置。
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============ 应用 ============
    app_name: str = Field(default="FastAPI Blog", description="应用名称")
    app_env: str = Field(default="dev", description="运行环境")
    app_debug: bool = Field(default=True, description="调试模式")
    app_host: str = Field(default="0.0.0.0", description="监听地址")
    app_port: int = Field(default=8000, description="监听端口")

    # ============ 数据库 ============
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=3306)
    db_user: str = Field(default="blog")
    db_password: str = Field(default="blog_pass")
    db_root_password: str = Field(default="root_pass")
    db_name: str = Field(default="blog")

    @property
    def database_url(self) -> str:
        """异步数据库连接 URL(SQLAlchemy 用)。"""
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def sync_database_url(self) -> str:
        """同步数据库连接 URL(Alembic 迁移用)。"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    # ============ 安全 ============
    secret_key: str = Field(
        default="change-me-to-a-long-random-string",
        description="JWT 签名密钥,生产环境务必改成随机长字符串",
    )
    access_token_expire_minutes: int = Field(
        default=1440, description="访问令牌过期时间(分钟)"
    )
    bcrypt_rounds: int = Field(default=12, description="bcrypt 哈希轮数")

    # ============ 日志 ============
    log_level: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取全局唯一的 Settings 实例(缓存)。"""
    return Settings()