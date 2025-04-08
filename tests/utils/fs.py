import os
from typing import Any

from localbook.lib.filesystem.dir import FSDir
from localbook.lib.filesystem.file import FSFile
from localbook.lib.filesystem.pdf import PDFFile


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


def mock_fsfile(path: str, parent: FSDir):
    return FSFile(path, parent, mime="text/plain", size=1, mtime=3.14)


def mock_pdffile(path: str, parent: FSDir):
    return PDFFile(path, parent, mime="application/pdf", size=1, mtime=3.14)


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
    root = FSDir(_rpath, None)
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
                mock_pdffile(
                    os.path.join(_rpath, name),
                    parent=root,
                )
            )
    return root
