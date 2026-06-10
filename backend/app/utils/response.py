from typing import TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

T = TypeVar("T")


def success_response(data: T = None, message: str = "success") -> dict[str, object]:
    return {"code": 0, "message": message, "data": jsonable_encoder(data)}


def error_response(code: int, message: str, status_code: int) -> JSONResponse:
    payload = {"code": code, "message": message, "data": None}
    return JSONResponse(status_code=status_code, content=payload)

