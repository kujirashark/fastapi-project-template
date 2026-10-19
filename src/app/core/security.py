"""安全工具:密码哈希 + JWT 签发/校验。"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings


def get_password_hash(password: str) -> str:
    """生成 bcrypt 密码哈希。"""
    settings = get_settings()
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验密码是否匹配哈希。"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # 哈希格式非法时按校验失败处理
        return False


def create_access_token(
    subject: str | int,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """签发 JWT。

    Args:
        subject: 令牌主体(通常是用户 id)
        extra_claims: 额外声明(角色、权限等)
        expires_delta: 自定义过期时间,不传则用配置项
    """
    settings = get_settings()
    now = datetime.now(UTC)
    expire = now + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    """解码 JWT。失败抛 JWTError。"""
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]
