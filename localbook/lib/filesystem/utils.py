# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 14:22
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import magic

from .node import FSNode


def _read_mime(arg: FSNode | str) -> str:
    try:
        if isinstance(arg, FSNode):
            filepath = arg._path
        elif isinstance(arg, str):
            filepath = arg

        with open(filepath, "rb") as f:
            KB = 1024
            bfile = f.read(KB * 10)
        mime = magic.from_buffer(bfile, mime=True)
        return mime
    except (magic.MagicException, FileNotFoundError, IsADirectoryError) as e:
        print(f"Error MIME-identification: {e}")
        return "unknown"
