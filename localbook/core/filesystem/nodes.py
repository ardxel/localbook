# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 17.03.2025 11:06
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from configparser import Error
from typing import Iterable, Optional, TypeGuard

import magic


class FSNode:
    def __init__(
        self,
        typo: str,
        path: str,
        parent: Optional["FSDir"] | None = None,
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


class FSFile(FSNode):
    def __init__(self, path: str, parent) -> None:
        super().__init__("f", path, parent)
        self.mime = _read_mime(self.path)

    def isfile(self) -> bool:
        return True


def is_fsfile(node: FSNode | None) -> TypeGuard[FSFile]:
    return isinstance(node, FSFile)


class FSDir(FSNode):
    def __init__(
        self,
        path: str,
        parent: Optional["FSDir"] = None,
        children: list[FSNode] | None = None,
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


class PDFFile(FSFile):
    def __init__(self, path: str, parent: Optional["FSDir"]) -> None:
        super().__init__(path, parent)
        if self.mime != "application/pdf":
            raise Error(
                f"Invalid file type for {self.path}: expected 'application/pdf', got '{self.mime}'."
            )
        self.size = os.stat(path).st_size
        basename = os.path.splitext(self.name)[0]
        self.cover_path = f"/static/img/{basename}.jpeg"


def _read_mime(arg: FSNode | str) -> str:
    try:
        if isinstance(arg, FSNode):
            filepath = arg.path
        elif isinstance(arg, str):
            filepath = arg

        with open(filepath, "rb") as f:
            KB = 1024
            bfile = f.read(KB * 10)
        mime = magic.from_buffer(bfile, mime=True)
        return mime
    except (magic.MagicException, FileNotFoundError, IsADirectoryError) as e:
        print(f"Error MIME-identification: {e}")
        return "unknown"


def is_pdf(arg: FSNode | str | None) -> bool:
    if arg is None:
        return False
    if isinstance(arg, FSNode):
        return isinstance(arg, PDFFile)
    if isinstance(arg, str):
        mime = _read_mime(arg)
        return mime == "application/pdf"
