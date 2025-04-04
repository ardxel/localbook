import os
from typing import Any
from unittest.mock import MagicMock, patch

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.pdf import PDFFile


def read_mime_side_effect(path: str):
    if path.endswith(".pdf"):
        return "application/pdf"
    else:
        return "text/plain"


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


def create_stub_tree(structure: dict[str, Any], _rpath: str = "/") -> FSDir:
    root = FSDir(_rpath, None)
    for name, content in structure.items():
        if isinstance(content, dict):
            root.children.append(create_stub_tree(content, os.path.join(_rpath, name)))
        elif content is None:
            with (
                patch("localbook.lib.filesystem.file.os.stat") as mock_stat,
                patch("localbook.lib.filesystem.file._read_mime") as mock_mime,
            ):
                mock_stat.return_value = MagicMock(st_size=1)
                mock_mime.side_effect = read_mime_side_effect

                root.children.append(
                    FSFile(
                        os.path.join(_rpath, name),
                        parent=root,
                    )
                )
        elif isinstance(content, str):
            with (
                patch("localbook.lib.filesystem.file.os.stat") as mock_stat,
                patch("localbook.lib.filesystem.file._read_mime") as mock_mime,
            ):
                mock_stat.return_value = MagicMock(st_size=1)
                mock_mime.side_effect = read_mime_side_effect
                root.children.append(
                    PDFFile(
                        os.path.join(_rpath, name),
                        parent=root,
                    )
                )
    return root
