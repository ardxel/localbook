# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import HTTPException, status

from localbook.lib.filesystem import file, node


class UnsupportedMediaTypeException(HTTPException):
    def __init__(self, node: node.FSNode) -> None:
        self.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        self.mime = node.mime if file.is_fsfile(node) else "Unsupported Media Type"


class NotFountException(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail if detail else "Not Found"


class BadRequestExpection(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = detail if detail else "Bad Request"
