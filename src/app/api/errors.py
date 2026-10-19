"""全局异常处理:把业务异常转成标准 HTTP 响应。"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import (
    AppException,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


def _make_error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details or None,
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details or None,
        )

    @app.exception_handler(AuthenticationError)
    async def auth_handler(_: Request, exc: AuthenticationError) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_handler(_: Request, exc: PermissionDeniedError) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(_: Request, exc: ConflictError) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.message,
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _make_error_response(
            status_code=422,
            error_code="request_validation_error",
            message="请求参数校验失败",
            details={"errors": exc.errors()},
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        """捕获 SQL 唯一约束等完整性错误,转成 409。"""
        return _make_error_response(
            status_code=409,
            error_code="db_integrity_error",
            message="数据完整性约束冲突",
            details={"reason": str(exc.orig)},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _make_error_response(
            status_code=exc.status_code,
            error_code="http_error",
            message=str(exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        # 生产环境应避免把 traceback 返回给客户端
        return _make_error_response(
            status_code=500,
            error_code="internal_error",
            message=f"服务器内部错误: {type(exc).__name__}",
        )