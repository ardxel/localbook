import sys
import tempfile
import unittest

from utils.fs import create_tmp_tree, get_all_nodes, get_tmp_struct

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.node import FSNode
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree, _FSTreeBuilder


class TestFSBuilder(unittest.TestCase):
    def test_build(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        create_tmp_tree(tmp_dir.name, get_tmp_struct())
        builder = _FSTreeBuilder(tmp_dir.name)
        fsdir = builder._build_tree()

        dir1: None | FSDir = None
        dir2: None | FSDir = None
        dir3: None | FSDir = None
        for n in fsdir.iter_children():
            if n.name == "dir1":
                dir1 = n
            if n.name == "dir2":
                dir2 = n
            if n.name == "dir3":
                dir3 = n

        self.assertIsNotNone(dir1)
        self.assertIsNotNone(dir2)
        self.assertIsNotNone(dir3)

        file1 = dir1.children[0]
        file2 = dir2.children[0]
        file3 = dir3.children[0].children[0]

        self.assertIsInstance(file1, FSFile)
        self.assertIsInstance(file2, FSFile)
        self.assertIsInstance(file3, FSFile)


class TestFSTree(unittest.TestCase):
    def test_max_depth(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        create_tmp_tree(tmp_dir.name, get_tmp_struct())

        depths = [1, 2, 3, sys.maxsize]
        trees = {d: FSTree(tmp_dir.name, max_depth=d) for d in depths}
        tmp_dir.cleanup()

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
                with self.subTest(depth=depth, path=path):
                    node = tree.get_node(path)
                    if expected_type is None:
                        self.assertIsNone(node)
                    else:
                        self.assertIsInstance(node, expected_type)
        tmp_dir.cleanup()

    def test_ignore_hidden(self):
        tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        tmp_struct = {
            "dir1": {".file1.txt": None},
            ".dir2": {"file2.txt": None},
        }
        create_tmp_tree(tmp_dir.name, tmp_struct)
        tree_ignore_hidden = FSTree(tmp_dir.name, ignore_hidden=True)
        tree_with_hidden = FSTree(tmp_dir.name, ignore_hidden=False)

        self.assertIsNone(tree_ignore_hidden.get_node("dir1/.file1.txt"))
        self.assertIsInstance(tree_with_hidden.get_node("dir1/.file1.txt"), FSFile)
        self.assertIsNone(tree_ignore_hidden.get_node(".dir2/file2.txt"))
        self.assertIsInstance(tree_with_hidden.get_node(".dir2/file2.txt"), FSFile)
        tmp_dir.cleanup()

    def test_get_node(self) -> None:
        with tempfile.TemporaryDirectory(prefix="localbook") as tmp_dir:
            create_tmp_tree(tmp_dir, get_tmp_struct())
            fstree = FSTree(tmp_dir)

            for node_path in get_all_nodes():
                node = fstree.get_node(node_path)
                self.assertIsNotNone(node)

    def test_parent(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        create_tmp_tree(tmp_dir.name, get_tmp_struct())
        fstree = FSTree(tmp_dir.name)
        parents_and_children = [
            ("dir1", "dir1/file1.txt"),
            ("dir2", "dir2/file2.txt"),
            ("dir3", "dir3/dir4"),
            ("dir3/dir4", "dir3/dir4/file3.txt"),
        ]

        for parent_path, child_path in parents_and_children:
            child_node = fstree.get_node(child_path)
            self.assertIsNotNone(child_node)
            if child_node is not None:  # type guard
                self.assertIsNotNone(child_node.parent)
                self.assertIs(fstree.get_node(parent_path), child_node.parent)
        tmp_dir.cleanup()

    def test_iterator(self) -> None:
        with tempfile.TemporaryDirectory(prefix="localbook") as tmp_dir:
            create_tmp_tree(tmp_dir, get_tmp_struct())
            fstree = FSTree(tmp_dir)
            tree_nodes = list(fstree.iter())
            self.assertTrue(len(tree_nodes) == len(get_all_nodes()))
