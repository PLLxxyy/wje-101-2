import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.utils.response import error_response

logger = logging.getLogger("coffeetaste.error")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "请求处理失败"
        return error_response(exc.status_code, message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("validation error on %s: %s", request.url.path, exc.errors())
        return error_response(422, "请求参数校验失败", 422)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("unhandled error on %s", request.url.path, exc_info=exc)
        return error_response(500, "服务器内部错误", 500)

