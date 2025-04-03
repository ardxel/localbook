# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 03.04.2025 12:19
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from typing import Iterable, Optional, TypeGuard

from .node import FSNode


class FSDir(FSNode):
    def __init__(
        self,
        path: str,
        parent: Optional["FSDir"] = None,
        children: Optional[list[FSNode]] = None,
    ) -> None:
        super().__init__("d", path, parent)
        self.children: list[FSNode] = children or []

    def isdir(self) -> bool:
        return True

    def iter_children(self) -> Iterable[FSNode]:
        for child in self.children:
            yield child


def is_fsdir(node: FSNode | None) -> TypeGuard[FSDir]:
    return isinstance(node, FSDir)
