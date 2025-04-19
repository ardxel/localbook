# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 11.04.2025 11:51
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import copy
import sys
import tempfile

from utils import create_tmp_tree

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.node import FSNode
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree, _FSTreeBuilder

tmp_struct = {
    "dir1": {"file1.txt": None},
    "dir2": {"file2.txt": None},
    "dir3": {"dir4": {"file3.txt": "tests/utils/test.pdf"}},
    "file4.txt": None,
}

all_nodes = [
    "dir1",
    "dir1/file1.txt",
    "dir2",
    "dir2/file2.txt",
    "dir3",
    "dir3/dir4",
    "dir3/dir4/file3.txt",
    "file4.txt",
]


class TestFSBuilder:
    def test_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            create_tmp_tree(tmp_dir, copy.deepcopy(tmp_struct))
            builder = _FSTreeBuilder(tmp_dir)
            fsdir = builder._build_tree()

        dir1: None | FSDir = None
        dir2: None | FSDir = None
        dir3: None | FSDir = None
        for n in fsdir.iter_children():
            if n.name == "dir1" and isinstance(n, FSDir):
                dir1 = n
            if n.name == "dir2" and isinstance(n, FSDir):
                dir2 = n
            if n.name == "dir3" and isinstance(n, FSDir):
                dir3 = n

        assert isinstance(dir1, FSDir)
        assert isinstance(dir2, FSDir)
        assert isinstance(dir3, FSDir)

        file1 = dir1.children[0]
        file2 = dir2.children[0]
        file3 = dir3.children[0].children[0]

        assert isinstance(file1, FSFile)
        assert isinstance(file2, FSFile)
        assert isinstance(file3, FSFile)


class TestFSTree:
    def test_max_depth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            create_tmp_tree(tmp_dir, copy.deepcopy(tmp_struct))
            depths = [1, 2, 3, sys.maxsize]
            trees = {d: FSTree(tmp_dir, max_depth=d) for d in depths}

        # table of expected values (depth -> path -> type of node)
        expected = {
            1: {
                "dir1": None,
                "dir1/file1.txt": None,
                "dir2": None,
                "dir2/file2.txt": None,
                "dir3": None,
                "dir3/dir4": None,
                "dir3/dir4/file3.txt": None,
                "file4.txt": FSFile,
            },
            2: {
                "dir1": FSDir,
                "dir1/file1.txt": FSNode,
                "dir2": FSNode,
                "dir2/file2.txt": FSNode,
                "dir3": None,
                "dir3/dir4": None,
                "dir3/dir4/file3.txt": None,
                "file4.txt": FSFile,
            },
            3: {
                "dir1": FSDir,
                "dir1/file1.txt": FSNode,
                "dir2": FSNode,
                "dir2/file2.txt": FSNode,
                "dir3": FSDir,
                "dir3/dir4": FSDir,
                "dir3/dir4/file3.txt": PDFFile,
                "file4.txt": FSFile,
            },
            sys.maxsize: {
                "dir1": FSDir,
                "dir1/file1.txt": FSNode,
                "dir2": FSNode,
                "dir2/file2.txt": FSNode,
                "dir3": FSDir,
                "dir3/dir4": FSDir,
                "dir3/dir4/file3.txt": PDFFile,
                "file4.txt": FSFile,
            },
        }

        for depth, paths in expected.items():
            tree = trees[depth]
            for path, expected_type in paths.items():
                node = tree.get_node(path)
                if expected_type is None:
                    assert node is None
                else:
                    assert isinstance(node, expected_type)

    def test_get_node(self) -> None:
        with tempfile.TemporaryDirectory(prefix="localbook") as tmp_dir:
            create_tmp_tree(tmp_dir, copy.deepcopy(tmp_struct))
            fstree = FSTree(tmp_dir)

            for node_path in copy.deepcopy(all_nodes):
                node = fstree.get_node(node_path)
                assert node is not None

    def test_parent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="localbook") as tmp_dir:
            create_tmp_tree(tmp_dir, copy.deepcopy(tmp_struct))
            fstree = FSTree(tmp_dir)
            parents_and_children = [
                ("dir1", "dir1/file1.txt"),
                ("dir2", "dir2/file2.txt"),
                ("dir3", "dir3/dir4"),
                ("dir3/dir4", "dir3/dir4/file3.txt"),
            ]

        for parent_path, child_path in parents_and_children:
            child_node = fstree.get_node(child_path)
            assert child_node is not None
            if child_node is not None:  # type guard
                assert child_node.parent is not None
                assert fstree.get_node(parent_path) is child_node.parent

    def test_iterator(self) -> None:
        with tempfile.TemporaryDirectory(prefix="localbook") as tmp_dir:
            create_tmp_tree(tmp_dir, copy.deepcopy(tmp_struct))
            fstree = FSTree(tmp_dir)
            tree_nodes = list(fstree.iter())
            assert len(tree_nodes) == len(copy.deepcopy(all_nodes))
