"""业务异常体系。

所有领域/服务层抛出的异常都继承这里,由 api/errors.py 统一转换为 HTTP 响应。
"""

from typing import Any


class AppException(Exception):  # noqa: N818 保留 Exception 后缀的领域惯例命名
    """所有业务异常的基类。"""

    status_code: int = 500
    error_code: str = "internal_error"
    default_message: str = "服务器内部错误"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源不存在。"""

    status_code = 404
    error_code = "not_found"
    default_message = "资源不存在"


class ValidationError(AppException):
    """业务校验失败(区别于 pydantic 的请求体验证)。"""

    status_code = 422
    error_code = "validation_error"
    default_message = "参数校验失败"


class AuthenticationError(AppException):
    """认证失败(未登录、token 无效等)。"""

    status_code = 401
    error_code = "authentication_error"
    default_message = "认证失败"


class PermissionDeniedError(AppException):
    """权限不足。"""

    status_code = 403
    error_code = "permission_denied"
    default_message = "权限不足"


class ConflictError(AppException):
    """资源冲突(唯一键重复等)。"""

    status_code = 409
    error_code = "conflict"
    default_message = "资源冲突"