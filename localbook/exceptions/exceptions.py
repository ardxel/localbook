# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import HTTPException, status


class UnsupportedMediaTypeException(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        self.detail = detail or "Unsupported media type"


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail or "Not Found"


class BadRequestExpection(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = detail or "Bad Request"
