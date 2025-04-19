# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 12:25
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from typing import Iterable

from pytest import fixture
from utils import create_stub_tree, get_tmp_struct, mock_fsdir, mock_fsfile

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.node import FSNode
from localbook.lib.filesystem.tree import _FSTreeNormalizer


class TestFSDir:

    @fixture
    def fsdir_tree(self):
        parent = mock_fsdir("/parent", None)
        child_dir = mock_fsdir("/parent/child", parent)
        file = mock_fsfile("/parent/file.pdf", parent)
        parent.children.extend([child_dir, file])
        return parent, child_dir, file

    def test_basic_properties(self, fsdir_tree):
        parent, child_dir, _ = fsdir_tree
        assert parent.name == "parent"
        assert parent.relpath == ""
        assert child_dir.relpath == "child"
        assert parent.isdir()
        assert len(parent.children) == 2

    def test_iter_children(self, fsdir_tree: tuple):
        parent, child_dir, file = fsdir_tree
        children = list(parent.iter_children())
        assert len(children) == 2
        assert child_dir in children
        assert file in children


class TestFSTreeNormalizer:
    def test_get_depth(self) -> None:
        structs = {
            2: {"dir1": {}},
            3: {"dir1": {"dir2": {}}},
            4: {"dir1": {"dir2": {"file1.pdf": None}}},
        }

        for depth, struct in structs.items():
            fsdir = create_stub_tree(struct)
            normalizer = _FSTreeNormalizer(fsdir)
            assert normalizer._get_depth(fsdir) == depth

    def test_drop_empty(self) -> None:
        struct1 = {"dir1": {"dir2": {}}}
        fsdir1 = create_stub_tree(struct1)
        normalizer = _FSTreeNormalizer(fsdir1)
        normalizer._drop_empty(fsdir1)
        assert not fsdir1.children

        struct2 = {"dir1": {"dir2": {"file1.txt": None}}}

        fsdir2 = create_stub_tree(struct2)
        assert fsdir2.children is not None
        assert fsdir2.children[0].children[0] is not None
        assert fsdir2.children[0].children[0].children[0] is not None

    def test_prune_depth(self) -> None:
        depths = [1, 2, 3, 4]

        for depth in depths:
            fsdir = create_stub_tree(get_tmp_struct())
            normalizer = _FSTreeNormalizer(fsdir)
            normalizer._prune(fsdir, depth)
            assert normalizer._get_depth(fsdir) == depth

    def test_exec(self) -> None:
        dir1 = mock_fsdir("/dir1", None)
        dir2 = mock_fsdir("/dir1/dir2", dir1)
        empty_dir = mock_fsdir("/dir1/empty_dir", dir1)
        dir3 = mock_fsdir("/dir1/dir2/dir3", dir2)
        file1 = mock_fsfile("/dir1/file1.txt", dir1)
        file2 = mock_fsfile("/dir1/dir2/file2.txt", dir2)
        file3 = mock_fsfile("/dir1/dir2/dir3/file3.txt", dir3)
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

        assert has(lambda x: x.name == "file1.txt", dir1.children)
        assert has(lambda x: x.name == "file2.txt", dir2.children)
        assert not has(lambda x: x.name == "file3.txt", dir3.children)
        assert has(lambda x: x.name == "empty_dir", dir1.children)
