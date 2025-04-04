import unittest
from typing import Iterable
from unittest.mock import MagicMock, patch

from utils.fs import create_stub_tree, get_tmp_struct
from utils.fs import read_mime_side_effect as mime_side_effect

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.node import FSNode
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree, _FSTreeNormalizer


class TestFSDir(unittest.TestCase):
    @patch("localbook.lib.filesystem.file._read_mime", side_effect=mime_side_effect)
    @patch("localbook.lib.filesystem.file.os.stat", return_value=MagicMock(st_size=1))
    def setUp(self, mock_os_stat, mock_get_mime):
        self.parent = FSDir("/parent", None)
        self.child_dir = FSDir("/parent/child", self.parent)
        self.file = FSFile("/parent/file.pdf", self.parent)
        self.parent.children.extend([self.child_dir, self.file])

    def test_basic_properties(self):
        self.assertEqual(self.parent.name, "parent")
        self.assertEqual(self.parent.relpath, "")
        self.assertEqual(self.child_dir.relpath, "child")
        self.assertTrue(self.parent.isdir())
        self.assertEqual(len(self.parent.children), 2)

    def test_iter_children(self):
        children = list(self.parent.iter_children())
        self.assertEqual(len(children), 2)
        self.assertIn(self.child_dir, children)
        self.assertIn(self.file, children)


class TestFSTreeNormalizer(unittest.TestCase):
    def test_get_depth(self) -> None:
        structs = {
            2: {"dir1": {}},
            3: {"dir1": {"dir2": {}}},
            4: {"dir1": {"dir2": {"file1.pdf": None}}},
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

    @patch("localbook.lib.filesystem.file._read_mime", side_effect=mime_side_effect)
    @patch("localbook.lib.filesystem.file.os.stat", return_value=MagicMock(st_size=1))
    def test_exec(self, mock_stat, mock_mime) -> None:
        dir1 = FSDir("/dir1", None)
        dir2 = FSDir("/dir1/dir2", dir1)
        empty_dir = FSDir("/dir1/empty_dir", dir1)
        dir3 = FSDir("/dir1/dir2/dir3", dir2)
        file1 = FSFile("/dir1/file1.txt", dir1)
        file2 = FSFile("/dir1/dir2/file2.txt", dir2)
        file3 = FSFile("/dir1/dir2/dir3/file3.txt", dir3)
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


class TestFSTreeWithMocks(unittest.TestCase):
    @patch("localbook.lib.filesystem.tree._FSTreeBuilder.build")
    @patch("localbook.lib.filesystem.file._read_mime", side_effect=mime_side_effect)
    @patch("localbook.lib.filesystem.file.os.stat", return_value=MagicMock(st_size=1))
    def test_tree_build_and_node_map(self, mock_stat, mock_get_mime, mock_build):
        root = FSDir("/root", None)
        file1 = FSFile("/root/file1.txt", root)
        pdf1 = PDFFile("/root/book.pdf", root)

        child_dir = FSDir("/root/dir", root)
        file2 = FSFile("/root/dir/file2.txt", child_dir)

        root.children = [file1, pdf1, child_dir]
        child_dir.children = [file2]

        mock_build.return_value = root

        tree = FSTree("/root")

        # Assert: проверка, что ноды попали в node_map
        self.assertIn("file1.txt", tree.node_map)
        self.assertIn("book.pdf", tree.node_map)
        self.assertIn("dir", tree.node_map)
        self.assertIn("dir/file2.txt", tree.node_map)

        self.assertIsInstance(tree.get_node("book.pdf"), PDFFile)
        self.assertIsNone(tree.get_node("nonexistent.pdf"))

    @patch("localbook.lib.filesystem.tree._FSTreeBuilder.build")
    def test_pdf_list_returns_only_pdfs(self, mock_build):
        root = FSDir("/root", None)
        pdf = PDFFile("/root/document.pdf", root, "application/pdf", 1)
        txt = FSFile("/root/readme.txt", root, "text/plain", 2)

        root.children = [pdf, txt]
        mock_build.return_value = root

        tree = FSTree("/root")
        pdfs = tree.pdf_list()

        self.assertEqual(len(pdfs), 1)
        self.assertIs(pdfs[0], pdf)

    @patch("localbook.lib.filesystem.tree._FSTreeBuilder.build")
    @patch("localbook.lib.filesystem.file._read_mime", side_effect=mime_side_effect)
    @patch("localbook.lib.filesystem.file.os.stat", return_value=MagicMock(st_size=1))
    def test_root_relative_and_get_node(self, mock_stat, mock_mime, mock_build):
        root = FSDir("/root", None)
        file = FSFile("/root/sub/file.txt", root)
        file.relpath = "sub/file.txt"
        root.children = [file]

        mock_build.return_value = root
        tree = FSTree("/root")

        # вручную добавим в node_map
        tree.node_map[file.relpath] = file

        rel = tree.root_relative("/root/sub/file.txt")
        self.assertEqual(rel, "sub/file.txt")

        node = tree.get_node("sub/file.txt")
        self.assertIs(node, file)
