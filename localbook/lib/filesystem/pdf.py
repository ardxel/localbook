# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 13:17
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from typing import Optional, TypeGuard

from .dir import FSDir
from .file import FSFile
from .node import FSNode
from .utils import _read_mime


class PDFFile(FSFile):
    def __init__(self, path: str, parent: Optional["FSDir"]) -> None:
        super().__init__(path, parent)
        assert self.mime == "application/pdf"
        self.size = os.stat(path).st_size
        basename = os.path.splitext(self.name)[0]
        self.cover_path = f"/static/img/{basename}.jpeg"


def is_pdf(arg: FSNode | str | None) -> TypeGuard[PDFFile]:
    if arg is None:
        return False
    if isinstance(arg, FSNode):
        return isinstance(arg, PDFFile)
    if isinstance(arg, str):
        mime = _read_mime(arg)
        return mime == "application/pdf"
