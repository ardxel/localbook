# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 13:17
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from typing import Optional


class FSNode:
    def __init__(
        self,
        typo: str,
        path: str,
        parent: Optional["FSDir"] = None,
    ) -> None:
        self.typo = typo
        self.path = path
        self.parent = parent
        self.name = os.path.basename(path)
        self.relpath = ""
        if self.parent is not None:
            self.relpath = os.path.join(self.parent.relpath, self.name)

    def isfile(self) -> bool:
        return False

    def isdir(self) -> bool:
        return False
