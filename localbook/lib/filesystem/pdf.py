# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 03.04.2025 12:19
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from typing import Optional

from .dir import FSDir
from .file import FSFile
from .node import FSNode
from .utils import _read_mime


class PDFFile(FSFile):
    def __init__(
        self,
        path: str,
        parent: Optional["FSDir"],
        mime: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(path, parent, mime, **kwargs)


def is_pdf(arg: FSNode | str | None) -> bool:
    if arg is None:
        return False
    if isinstance(arg, FSNode):
        return isinstance(arg, PDFFile)
    if isinstance(arg, str):
        mime = _read_mime(arg)
        return mime == "application/pdf"
