# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:22
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
from typing import Any

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.node import NID
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree
from localbook.service.book.cover import _BookCoverInfo


def get_tmp_struct():
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


def mock_fsdir(path: str, parent: FSDir | None, _nid: str = "1"):
    return FSDir(
        path,
        parent=parent,
        size=1,
        mtime=3.14,
        _nid=_nid,
    )


def mock_fsfile(path: str, parent: FSDir, _nid: str = "1"):
    return FSFile(
        path,
        parent,
        mime="text/plain",
        size=1,
        mtime=3.14,
        _nid=_nid,
    )


def mock_pdf_file(path: str, parent: None | FSDir, _nid: str = "1"):
    return PDFFile(
        path,
        parent,
        mime="application/pdf",
        size=1,
        mtime=3.14,
        _nid=_nid,
    )


def mock_fstree(
    root: FSDir,
    max_depth: int = 999,
    ignore_hidden: bool = True,
    follow_symlink: bool = False,
):
    return FSTree(
        root,
        max_depth=max_depth,
        ignore_hidden=ignore_hidden,
        follow_symlink=follow_symlink,
    )


def mock_cover_info(
    path: str = "/root/test.pdf",
    pdf_nid: str = "1",
    thumbnails: dict[str, str] = {},
    mtime=3.14,
):
    return _BookCoverInfo(
        path,
        pdf_nid=NID(pdf_nid, hash=False),
        thumbnails=thumbnails,
        mtime=mtime,
    )


def create_tmp_tree(base_dir: str, structure: dict[str, Any]) -> None:
    for name, content in structure.items():
        current_path = os.path.join(base_dir, name)

        if isinstance(content, dict):
            os.makedirs(current_path, exist_ok=True)
            create_tmp_tree(current_path, content)
        elif content is None:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w") as f:
                f.write(name)
        elif isinstance(content, str):
            os.makedirs(os.path.dirname(current_path), exist_ok=True)

            if not os.path.exists(content):
                print("File is not exist")
                continue

            with open(content, "rb") as original:
                with open(current_path, "wb") as fake:
                    fake.write(original.read())


def create_stub_tree(
    structure: dict[str, Any],
    _rpath: str = "/",
) -> FSDir:
    root = mock_fsdir(_rpath, None)
    for name, content in structure.items():
        if isinstance(content, dict):
            root.children.append(create_stub_tree(content, os.path.join(_rpath, name)))
        elif content is None:
            root.children.append(
                mock_fsfile(
                    os.path.join(_rpath, name),
                    parent=root,
                )
            )
        elif isinstance(content, str):
            root.children.append(
                mock_pdf_file(
                    os.path.join(_rpath, name),
                    parent=root,
                )
            )
    return root
