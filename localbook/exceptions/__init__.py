# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 13:55
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import status
from starlette.types import ExceptionHandler

from .handlers import not_found_handler, unsupported_media_type_handler


class LBExceptionHandler:
    def __init__(self, status_code: int, handler: ExceptionHandler) -> None:
        self.status_code = status_code
        self.handler = handler


exception_handlers = [
    LBExceptionHandler(
        status_code=status.HTTP_404_NOT_FOUND,
        handler=not_found_handler,
    ),
    LBExceptionHandler(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        handler=unsupported_media_type_handler,
    ),
]
