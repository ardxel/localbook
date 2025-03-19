# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 17:21
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import HTTPException, status, templating
from fastapi.responses import JSONResponse

from localbook.lib.filesystem.nodes import FSFile, FSNode, is_fsfile


class UnsupportedMediaTypeException(HTTPException):
    def __init__(self, node: FSNode) -> None:
        self.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        self.mime = node.mime if is_fsfile(node) else "unknown"


class NotFountException(HTTPException):
    def __init__(self, detail: str = "") -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        if detail:
            self.detail = detail
        else:
            self.detail = "Not found"
