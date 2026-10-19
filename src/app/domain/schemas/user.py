"""User 相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """User 公共字段。"""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """注册请求。"""

    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    """更新用户请求(全部可选)。"""

    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)


class UserOut(UserBase):
    """用户响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str  # 用户名或邮箱
    password: str


class TokenResponse(BaseModel):
    """登录响应:JWT。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒