import os
import sys
import tempfile
import unittest

from utils.stub_tree import create_stub_tree

from localbook.lib.filesystem.tree import FSTree


def get_stub_struct():
    return {
        "dir1": {"file1.txt": None},
        "dir2": {"file2.txt": None},
        "dir3": {"dir4": {"file3.txt": "tests/utils/test.pdf"}},
        "file4.txt": None,
    }


def get_all_nodes():
    return [
        "dir1",
        "dir1/file1.txt",
        "dir2",
        "dir2/file2.txt",
        "dir3",
        "dir3/dir4",
        "dir3/dir4/file3.txt",
        "file4.txt",
    ]


class TestFSTreeDepth(unittest.TestCase):
    def test_depth(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        create_stub_tree(tmp_dir.name, get_stub_struct())

        trees = {
            1: FSTree(tmp_dir.name, max_depth=1),
            2: FSTree(tmp_dir.name, max_depth=2),
            3: FSTree(tmp_dir.name, max_depth=3),
            sys.maxsize: FSTree(tmp_dir.name),
        }

        for node_path in get_all_nodes():
            parts = node_path.split(os.path.sep)
            node_depth = len(parts)
            for max_depth, tree in trees.items():
                with self.subTest(node=node_path, max_depth=max_depth):
                    if max_depth > node_depth:
                        self.assertIsNotNone(tree.get_node(node_path))
                    elif max_depth == node_depth:
                        if "file" in os.path.basename(node_path):
                            self.assertIsNotNone(tree.get_node(node_path))
                        else:
                            self.assertIsNone(tree.get_node(node_path))
                    else:
                        self.assertIsNone(tree.get_node(node_path))


class TestFSTreeGetNode(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory(prefix="localbook")
        create_stub_tree(self.tmp_dir.name, get_stub_struct())
        self.fstree = FSTree(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_get_node(self) -> None:
        for node_path in get_all_nodes():
            node = self.fstree.get_node(node_path)
            self.assertIsNotNone(node)

    def test_parent(self) -> None:
        parents_and_children = [
            ("dir1", "dir1/file1.txt"),
            ("dir2", "dir2/file2.txt"),
            ("dir3", "dir3/dir4"),
            ("dir3/dir4", "dir3/dir4/file3.txt"),
        ]

        for parent_path, child_path in parents_and_children:
            child_node = self.fstree.get_node(child_path)
            self.assertIsNotNone(child_node)
            if child_node is not None:  # type guard
                self.assertIsNotNone(child_node.parent)
                self.assertIs(self.fstree.get_node(parent_path), child_node.parent)

    def test_iterator(self) -> None:
        all_nodes_from_iter = list(self.fstree.iter_children(recursive=True))
        self.assertTrue(len(all_nodes_from_iter) == len(get_all_nodes()))
