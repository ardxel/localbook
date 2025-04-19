# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:23
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import copy
import os
import shutil
import tempfile
from copy import deepcopy

from utils import create_tmp_tree

from localbook.lib.filesystem.tree import FSTree
from localbook.service.book.cover import (
    DEFAULT_IMAGE_SETTINGS,
    BookCoverGenerator,
    BookCoverMetadata,
    _BookCoverInfo,
)

basic_thumbnails = {
    "desktop": "file/desktop.jpeg",
    "mobile": "file/mobile.jpeg",
    "laptop": "file/laptop.jpeg",
    "tablet": "file/tablet.jpeg",
}

cover_data = [
    _BookCoverInfo(
        "/root/file1.pdf",
        pdf_nid="hash1",
        thumbnails=basic_thumbnails.copy(),
        mtime=0.1,
    ),
    _BookCoverInfo(
        "/root/file2.pdf",
        pdf_nid="hash1",
        thumbnails=basic_thumbnails.copy(),
        mtime=0.1,
    ),
    _BookCoverInfo(
        "/root/file3.pdf",
        pdf_nid="hash1",
        thumbnails=basic_thumbnails.copy(),
        mtime=0.1,
    ),
]


class TestBookCoverMetadata:
    def test_metadata(self):
        tmp_file = tempfile.NamedTemporaryFile(prefix="localbook_metadata")
        metadata = BookCoverMetadata(tmp_file.name)
        metadata.save(deepcopy(cover_data))
        parsed_data = metadata.read()

        for initial, parsed in zip(cover_data, parsed_data.covers):
            assert initial.original == parsed.original
            assert initial.pdf_nid == parsed.pdf_nid
            assert initial.thumbnails == parsed.thumbnails
            assert initial.mtime == parsed.mtime


class TestBookCoverGenerator:
    test_pdf = "tests/utils/test.pdf"
    tmp_struct1 = {
        "file1.pdf": test_pdf,
        "dir1": {"file2.pdf": test_pdf},
        "dir2": {"dir3": {"file3.pdf": test_pdf}},
    }
    tmp_struct2 = {
        "file1.pdf": test_pdf,
        "dir2": {"dir3": {"file3.pdf": test_pdf}},
    }

    image_settings = [{**k, "dpi": 1, "quality": 1} for k in DEFAULT_IMAGE_SETTINGS]

    def test_generator(self):

        tree_dir = tempfile.TemporaryDirectory(prefix="tree")
        tmp_root = tempfile.TemporaryDirectory(prefix="cover")
        tmp_root_covers = os.path.join(tmp_root.name, "covers")
        metadata_file = os.path.join(tmp_root.name, "metadata.json")
        create_tmp_tree(tree_dir.name, copy.deepcopy(self.tmp_struct1))

        fstree1 = FSTree(tree_dir.name)
        metadata = BookCoverMetadata(metadata_file)
        generator_no_artefact = BookCoverGenerator(
            tmp_root_covers,
            image_settings=copy.deepcopy(self.image_settings),
            fstree=fstree1,
            metadata=metadata,
        )
        generator_no_artefact.generate(cache=False)
        fstree1 = generator_no_artefact.fstree

        files = [
            fstree1.get_node("file1.pdf"),
            fstree1.get_node("dir1/file2.pdf"),
            fstree1.get_node("dir2/dir3/file3.pdf"),
        ]

        for file in files:
            assert file is not None

        old_cover_mtimes: dict[str, float] = {}
        for cover_dir in os.scandir(tmp_root_covers):
            dp = cover_dir.path
            old_cover_mtimes[dp] = os.path.getmtime(dp)

        # recreate tree_dir for fstree
        shutil.rmtree(tree_dir.name)
        create_tmp_tree(tree_dir.name, copy.deepcopy(self.tmp_struct2))

        fstree2 = FSTree(tree_dir.name)
        metadata_file = os.path.join(tmp_root.name, "metadata.json")
        metadata = BookCoverMetadata(metadata_file)
        generator_with_artefact = BookCoverGenerator(
            tmp_root_covers,
            image_settings=copy.deepcopy(self.image_settings),
            fstree=fstree2,
            metadata=metadata,
        )
        generator_with_artefact.generate(cache=True)

        files = [
            fstree2.get_node("file1.pdf"),
            fstree2.get_node("dir2/dir3/file3.pdf"),
        ]

        for file in files:
            assert file is not None

        updated_cover_mtimes: dict[str, float] = {}
        for cover_dir in os.scandir(tmp_root_covers):
            dp = cover_dir.path
            updated_cover_mtimes[dp] = os.path.getmtime(dp)

        # assert old mtime cover dirs with updated mtime cover dirs
        # to check the directories are really cached and not overrited
        assert len(old_cover_mtimes) > len(updated_cover_mtimes)

        for path, mtime in updated_cover_mtimes.items():
            assert old_cover_mtimes[path] == mtime
