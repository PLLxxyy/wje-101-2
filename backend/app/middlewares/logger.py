import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request

logger = logging.getLogger("coffeetaste.request")


async def logger_middleware(request: Request, call_next: Callable[[Request], Awaitable[object]]) -> object:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    query = str(request.url.query)
    status_code = getattr(response, "status_code", 500)
    logger.info("%s %s?%s %s %sms", request.method, request.url.path, query, status_code, elapsed_ms)
    return response

