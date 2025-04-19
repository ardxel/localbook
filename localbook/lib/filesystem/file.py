# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 03.04.2025 12:19
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

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
        **kwargs,
    ) -> None:
        super().__init__(path, parent, **kwargs, typo="f")
        self.mime = mime or _read_mime(self._path)

    def isfile(self) -> bool:
        return True


def is_fsfile(node: FSNode | None) -> TypeGuard[FSFile]:
    """type guard function"""
    return isinstance(node, FSFile)
