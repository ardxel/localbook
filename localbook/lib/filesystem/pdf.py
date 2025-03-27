# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 13:17
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from typing import Optional

from .dir import FSDir
from .file import FSFile
from .node import FSNode
from .utils import _read_mime


class PDFFile(FSFile):
    def __init__(self, path: str, parent: Optional["FSDir"]) -> None:
        super().__init__(path, parent)
        if self.mime != "application/pdf":
            raise Exception(
                f"Invalid file type for {self.path}: expected 'application/pdf', got '{self.mime}'."
            )
        self.size = os.stat(path).st_size
        basename = os.path.splitext(self.name)[0]
        self.cover_path = f"/static/img/{basename}.jpeg"


def is_pdf(arg: FSNode | str | None) -> bool:
    if arg is None:
        return False
    if isinstance(arg, FSNode):
        return isinstance(arg, PDFFile)
    if isinstance(arg, str):
        mime = _read_mime(arg)
        return mime == "application/pdf"
