# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 07:03
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import logging
import os
import sys
from typing import Iterable

from .nodes import FSDir, FSFile, FSNode, PDFFile, is_fsdir, is_fsfile, is_pdf

logger = logging.getLogger("localbook")


def _build_tree(root_path: str, max_depth=sys.maxsize) -> FSDir:
    root_node = FSDir(root_path, None)
    stack = [(root_node, root_path, 1)]
    while stack:
        parent_node, current_path, depth = stack.pop()
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if entry.is_file():
                        node = (
                            PDFFile(entry.path, parent_node)
                            if is_pdf(entry.path)
                            else FSFile(entry.path, parent_node)
                        )
                    elif entry.is_dir() and depth < max_depth:
                        node = FSDir(entry.path, parent_node)
                        stack.append((node, entry.path, depth + 1))
                    else:

                        continue
                    parent_node.children.append(node)
        except PermissionError:
            pass
    return root_node


class FSTree:
    def __init__(self, root: str, max_depth=3) -> None:
        self.root_node = _build_tree(root, max_depth)
        self.node_map: dict[str, FSNode] = {}
        stack: list[FSNode] = [self.root_node]
        while stack:
            node = stack.pop()
            if node.isdir() and isinstance(node, FSDir):
                stack.extend(node.iter_children())

            self.node_map[node.relpath] = node

    def get_root_node(self) -> FSDir:
        return self.root_node

    def root_relative(self, path: str) -> str:
        return os.path.relpath(path, self.root_node.path)

    def get_node(self, path: str) -> FSNode | None:
        return self.node_map.get(path)

    def iter_children(
        self,
        dir_node: FSDir | None = None,
        recursive=False,
        ignore_dir_node=False,
    ) -> Iterable[FSNode]:
        if dir_node is None:
            dir_node = self.get_root_node()
        if ignore_dir_node:
            yield dir_node
        for node in dir_node.iter_children():
            if is_fsdir(node):
                if recursive:
                    yield from self.iter_children(node)
                if ignore_dir_node:
                    continue
                else:
                    yield node
            else:
                yield node
