import copy
import tempfile
import unittest
from shutil import rmtree

from stub.tree import stub_tree

from fs import FSTree

temp_root = "/tmp"
stub_struct = {
    "dir1": {"file1.txt": None},
    "dir2": {"file2.txt": None},
    "file3.txt": None,
}


def create_temp_tree() -> FSTree:
    temp_dir = tempfile.mkdtemp("localbook")
    stub_tree(temp_dir, copy.deepcopy(stub_struct))
    t = FSTree(temp_dir)
    rmtree(temp_dir)
    return t


class TestFS(unittest.TestCase):

    def test_instance(self):
        tree = create_temp_tree()
        self.assertIsInstance(tree, FSTree)

    def test_get_node(self):
        tree = create_temp_tree()

        dir1 = tree.get_node("dir1")
        dir2 = tree.get_node("dir2")
        file1 = tree.get_node("dir1/file1.txt")
        file2 = tree.get_node("dir2/file2.txt")
        file3 = tree.get_node("file3.txt")

        self.assertIsNotNone(dir1)
        self.assertIsNotNone(dir2)
        self.assertIsNotNone(file1)
        self.assertIsNotNone(file2)
        self.assertIsNotNone(file3)


if __name__ == "__main__":
    unittest.main()
