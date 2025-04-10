# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 03.04.2025 12:19
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from typing import Optional, TypeGuard

from .dir import FSDir
from .node import FSNode
from .utils import _read_mime


class FSFile(FSNode):
    def __init__(
        self,
        path: str,
        parent: Optional[FSDir],
        mime: Optional[str] = None,
        size: Optional[int] = None,
        mtime: Optional[float] = None,
        **kwargs,
    ) -> None:
        super().__init__("f", path, parent, **kwargs)
        self.mime = mime or _read_mime(self._path)
        self.size = size or os.stat(path).st_size
        self.mtime = mtime or os.path.getmtime(path)

    def isfile(self) -> bool:
        return True


def is_fsfile(node: FSNode | None) -> TypeGuard[FSFile]:
    """type guard function"""
    return isinstance(node, FSFile)
