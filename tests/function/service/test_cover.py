# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:23
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import copy
import os
import tempfile

from utils import create_tmp_tree

from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree
from localbook.service.book.cover import (
    DEFAULT_IMAGE_SETTINGS,
    BookCoverGenerator,
    BookCoverMetadata,
    BookCoverService,
)

test_pdf = "tests/utils/test.pdf"
tmp_struct = {
    "file1.pdf": test_pdf,
    "dir1": {"file2.pdf": test_pdf},
    "dir2": {"dir3": {"file3.pdf": test_pdf}},
}


class TestBookCoverService:
    def test_service(self):
        tree_dir = tempfile.TemporaryDirectory(prefix="tree")
        create_tmp_tree(tree_dir.name, copy.deepcopy(tmp_struct))
        fstree = FSTree(tree_dir.name)

        tmp_root = tempfile.TemporaryDirectory(prefix="cover")
        tmp_root_covers = os.path.join(tmp_root.name, "covers")
        metadata_file = os.path.join(tmp_root.name, "metadata.json")
        metadata = BookCoverMetadata(metadata_file)
        generator = BookCoverGenerator(
            tmp_root_covers,
            image_settings=DEFAULT_IMAGE_SETTINGS,
            fstree=fstree,
            metadata=metadata,
        )
        generator.generate(cache=False)
        service = BookCoverService(metadata)

        pdf_files = [
            fstree.get_node("file1.pdf"),
            fstree.get_node("dir1/file2.pdf"),
            fstree.get_node("dir2/dir3/file3.pdf"),
        ]

        for pdf in pdf_files:
            assert isinstance(pdf, PDFFile)
            for s in DEFAULT_IMAGE_SETTINGS:
                cover_fp = service.get_cover(pdf, s["device"])
                expected_fp = os.path.join(
                    tmp_root_covers,
                    pdf.nid,
                    f"{s["device"]}.{s["format"].lower()}",
                )
                assert cover_fp == expected_fp
        tree_dir.cleanup()
        tmp_root.cleanup()
