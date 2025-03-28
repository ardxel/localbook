# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 13:15
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from typing import TypeGuard

from .node import FSNode
from .utils import _read_mime


class FSFile(FSNode):
    def __init__(self, path: str, parent) -> None:
        super().__init__("f", path, parent)
        self.mime = _read_mime(self._path)

    def isfile(self) -> bool:
        return True


def is_fsfile(node: FSNode | None) -> TypeGuard[FSFile]:
    """type guard function"""
    return isinstance(node, FSFile)
