import unittest
from typing import Iterable

from utils.fs import create_stub_tree, create_tmp_tree, get_all_nodes, get_tmp_struct

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.node import FSNode
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree, _FSTreeNormalizer


class TestFSTreeNormalizer(unittest.TestCase):

    def test_get_depth(self) -> None:
        structs = {
            2: {"dir1": {}},
            3: {"dir1": {"dir2": {}}},
            4: {"dir1": {"dir2": {"file1.txt": None}}},
        }

        for depth, struct in structs.items():
            with self.subTest(depth=depth):
                fsdir = create_stub_tree(struct)
                normalizer = _FSTreeNormalizer(fsdir)
                self.assertIs(normalizer._get_depth(fsdir), depth)

    def test_drop_empty(self) -> None:
        struct1 = {
            "dir1": {"dir2": {}},
        }

        fsdir1 = create_stub_tree(struct1)
        normalizer = _FSTreeNormalizer(fsdir1)
        normalizer._drop_empty(fsdir1)
        self.assertFalse(fsdir1.children)

        struct2 = {
            "dir1": {"dir2": {"file1.txt": None}},
        }

        fsdir2 = create_stub_tree(struct2)
        self.assertIsNotNone(fsdir2.children)
        self.assertIsNotNone(fsdir2.children[0].children[0])
        self.assertIsNotNone(fsdir2.children[0].children[0].children[0])

    def test_prune_depth(self) -> None:
        depths = [1, 2, 3, 4]

        for depth in depths:
            with self.subTest(depth=depth):
                fsdir = create_stub_tree(get_tmp_struct())
                normalizer = _FSTreeNormalizer(fsdir)
                normalizer._prune(fsdir, depth)
                self.assertIs(normalizer._get_depth(fsdir), depth)

    def test_exec(self) -> None:
        dir1 = FSDir("/dir1", None)
        dir2 = FSDir("/dir1/dir2", dir1)
        empty_dir = FSDir("/dir1/empty_dir", dir1)
        dir3 = FSDir("/dir1/dir2/dir3", dir2)
        file1 = FSFile("/dir1/file1.txt", dir1, "text/plain", 1)
        file2 = FSFile("/dir1/dir2/file2.txt", dir2, "text/plain", 1)
        file3 = FSFile("/dir1/dir2/dir3/file3.txt", dir3, "text/plain", 1)
        dir1.children.extend([dir2, empty_dir, file1])
        dir2.children.extend([dir3, file2])
        dir3.children.extend([file3])

        normalizer = _FSTreeNormalizer(dir1, max_depth=3, remove_empty_dirs=False)
        normalizer.exec()

        def has(fn, iter: Iterable[FSNode]) -> bool:
            for item in iter:
                if fn(item):
                    return True
            return False

        self.assertTrue(has(lambda x: x.name == "file1.txt", dir1.children))
        self.assertTrue(has(lambda x: x.name == "file2.txt", dir2.children))
        self.assertFalse(has(lambda x: x.name == "file3.txt", dir3.children))
        self.assertTrue(has(lambda x: x.name == "empty_dir", dir1.children))


class TestFSTreeBuilder(unittest.TestCase):
    pass
