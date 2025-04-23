# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import collections
import logging
import os
import sys
from typing import Iterable, Optional

from .dir import FSDir, is_fsdir
from .file import FSFile, is_fsfile
from .node import FSNode
from .pdf import PDFFile, is_pdf

logger = logging.getLogger("localbook")


class _FSTreeNormalizer:
    def __init__(
        self,
        root: FSDir,
        max_depth: Optional[int] = None,
        remove_empty_dirs=True,
    ) -> None:
        self.__root = root
        self.max_depth = max_depth
        self.check_depth = max_depth is not None
        self.remove_empty_dirs = remove_empty_dirs

    def _get_depth(self, root: FSDir) -> int:
        max_d = 1
        q = collections.deque([(root, 1)])
        while q:
            fsdir, depth = q.popleft()
            max_d = max(max_d, depth)
            for n in fsdir.iter_children():
                if is_fsdir(n):
                    q.append((n, depth + 1))
                else:
                    max_d = max(max_d, depth + 1)
        return max_d

    def _prune(self, root: FSDir, max_depth: int, _current_depth=1) -> None:
        """Prune the tree to a specific depth."""
        if _current_depth >= max_depth:
            root.children = []
            return
        for n in root.iter_children():
            if is_fsdir(n):
                self._prune(n, max_depth, _current_depth + 1)

    def _drop_empty(self, root: FSDir) -> bool:
        """Remove empty FSDir nodes recursively in place.

        Empty directories are removed from the tree

        Args:
            root (FSDir): filesystem directory
        Returns:
            bool: FSDir.children is empty or not
        """
        nodes = list(root.iter_children())
        if not nodes:
            return True
        normalized_nodes: list[FSNode] = []
        for node in nodes:
            if is_fsdir(node):
                is_empty = self._drop_empty(node)
                if not is_empty:
                    normalized_nodes.append(node)
            else:
                normalized_nodes.append(node)
        root.children = normalized_nodes
        return not normalized_nodes

    def exec(self) -> None:
        if self.check_depth:
            real_depth = self._get_depth(self.__root)
            if real_depth > self.check_depth and self.max_depth:
                self._prune(self.__root, max_depth=self.max_depth)
        if self.remove_empty_dirs:
            self._drop_empty(self.__root)


class _FSTreeBuilder:
    def __init__(
        self,
        root: str | FSDir,
        max_depth=sys.maxsize,
        follow_symlink=False,
        ignore_hidden=True,
        normalize=True,
    ) -> None:
        """
        Args:
            root (str | FSDir): root dir or already builded FSDir
            max_depth (int): max depth of diving through filesystem tree
            follow_symlink (bool): follow symlinks
            ignore_hidden (bool): ignore dotfiles
            normalize (bool): ignore empty directories
        """
        if isinstance(root, FSDir):
            self.__fsdir: None | FSDir = root
            self.__rpath = None
        else:
            self.__fsdir = None
            self.__rpath: None | str = root
        self.max_depth = max_depth
        self.follow_symlink = follow_symlink
        self.ignore_hidden = ignore_hidden
        self.normalize = normalize

    def _create_node(self, x: str, parent: FSDir) -> FSNode | None:
        """create an instance based on the proposed path of entry.

        Only files and directory are processed.
        """
        if os.path.isfile(x):
            if is_pdf(x):
                return PDFFile(x, parent)
            return FSFile(x, parent)
        elif os.path.isdir(x):
            return FSDir(x, parent)
        else:  # ignore other type of files
            return None

    def _filter_hidden(self, entries: Iterable[str]) -> list[str]:
        """return new list without dotfiles"""
        return [x for x in entries if not os.path.basename(x).startswith(".")]

    # def _normalize_tree(self) -> None:
    #     if self.root_node is not None:
    #         need_to_check_depth = isinstance(self.__rpath, FSDir)
    #         normalizer = _FSTreeNormalizer(
    #             self.root_node,
    #             max_depth=self.max_depth if need_to_check_depth else None,
    #             remove_empty_dirs=True,
    #         )
    #         normalizer.exec()

    def _build_tree(self) -> FSDir:
        # no  need to build if `root` is already FSDir
        if self.__rpath is None:
            raise ValueError("Missing __rpath argument.")

        self.root_node = FSDir(self.__rpath, None)
        queue = collections.deque([(self.root_node, self.__rpath, 1)])
        visited: set[str] = set()  # visited absolute paths if reads symlink
        while queue:
            parent_node, current_path, depth = queue.popleft()
            try:
                entries = [entry.path for entry in os.scandir(current_path)]
            except PermissionError:
                continue

            if self.ignore_hidden:
                entries = self._filter_hidden(entries)

            for entry in entries:
                if os.path.islink(entry):
                    if not self.follow_symlink:
                        continue
                    real_entry = os.path.realpath(entry)
                    if real_entry in visited:
                        continue
                    entry = real_entry

                node = self._create_node(entry, parent_node)
                if not node:
                    continue

                if is_fsfile(node) and depth <= self.max_depth:
                    parent_node.children.append(node)
                elif is_fsdir(node) and depth < self.max_depth:
                    queue.append((node, node._path, depth + 1))
                    parent_node.children.append(node)
        return self.root_node

    def build(self) -> FSDir:
        try:
            fsdir = self.__fsdir or self._build_tree()
            normalizer = _FSTreeNormalizer(
                fsdir,
                max_depth=self.__fsdir and self.max_depth or None,
                remove_empty_dirs=True,
            )
            normalizer.exec()
            return fsdir

        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.error(f"_FSTreeBuilder failed: {e}")
            raise
        except Exception as e:
            logger.exception("Unexpected error is _FSTreeBuilder")
            raise


class FSTree:
    """Class for filesystem presentation in tree view

    The 'FSTree' reads the file structure representing each element in the form of a node.
    Each node can be obtained along the path of this very element.

    Attributes:
        root_node (FSDir): root node of the tree

    """

    def __init__(
        self,
        root: str | FSDir,
        max_depth=sys.maxsize,
        ignore_hidden=True,
        follow_symlink=True,
        normalize=True,
    ) -> None:
        """
        Args:
            root (str|FSDir): main entry of filesystem tree, can be str(path)
                or `FSDir`
            max_depth (int): max depth of recursive diving. counter
                starts from 1
        """
        self.max_depth = max_depth
        self.builder_args = {
            "max_depth": max_depth,
            "ignore_hidden": ignore_hidden,
            "follow_symlink": follow_symlink,
            "normalize": normalize,
        }
        tree_builder = _FSTreeBuilder(root, **self.builder_args)
        self.root_node = tree_builder.build()
        if self.root_node is None:
            logger.exception("FSTree build error")
            return
        self.node_map: dict[str, FSNode] = {}
        stack: list[FSNode] = [self.root_node]
        while stack:
            node = stack.pop()
            if node.isdir() and isinstance(node, FSDir):
                stack.extend(node.iter_children())

            self.node_map[node.relpath] = node

    def get_root_node(self) -> FSDir:
        """returns root node"""
        return self.root_node

    def root_relative(self, path: str) -> str:
        return os.path.relpath(path, self.root_node._path)

    def get_node(self, path: str) -> FSNode | None:
        """returns node by special relative path"""
        normalized_path = os.path.normpath(path)  # remove possible ".." in path
        full_path = os.path.join(self.root_node._path, normalized_path)
        if not full_path.startswith(self.root_node._path):
            return None

        return self.node_map.get(path)

    def iter(
        self,
    ) -> Iterable[FSNode]:
        """Return FSTree Iterator[FSNode]"""
        for node in filter(lambda x: x.relpath != "", self.node_map.values()):
            yield node

    def pdf_list(self) -> list[PDFFile]:
        return [f for f in self.iter() if isinstance(f, PDFFile)]

    def debug(self) -> None:
        print("##################")
        print(f"Tree root: {self.root_node._path}")
        print("Options:")
        for opt, val in self.builder_args.items():
            print(f"  {opt}={val}")
        print("Nodes:")
        for n in self.iter():
            print(f"  {n.relpath}")
        print("##################")
