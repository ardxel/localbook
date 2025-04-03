# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 03.04.2025 12:19
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import itertools
import os
from typing import Optional


class nid(int):
    def __new__(cls, value: int):
        return super().__new__(cls, value)


class FSNode:
    _node_counter = itertools.count()

    def __init__(
        self,
        typo: str,
        path: str,
        parent: Optional["FSNode"] = None,
    ) -> None:
        self.nid: nid = nid(next(FSNode._node_counter))
        # type of node: file or directory: "f" | "d"
        self.typo = typo
        self._path = path
        self.parent = parent
        self.name = os.path.basename(path)
        # `relpath` is a trimmed absolute path to prevent the client
        # from seeing real system paths.
        # Users can access files and directories only via this relative path.
        # For example, if the app configuration specifies `user_data_location = "home/user/books"`,
        # the main entry point will be "/".
        # All nodes in the filesystem tree (FSTree) are stored relative to this root.
        # For instance, if a file has an absolute path `/home/user/books/a/b/c/file.txt`,
        # it can only be accessed via `relpath = "a/b/c/file.txt"`.
        self.relpath = ""
        if self.parent is not None:
            self.relpath = os.path.join(self.parent.relpath, self.name)

    def isfile(self) -> bool:
        return False

    def isdir(self) -> bool:
        return False
