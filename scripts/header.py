# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import glob
import os
import re
from datetime import datetime as dt

from _config import git_root


def header(mtime: str) -> str:
    return "\n".join(
        [
            "# ================================================================",
            "# @Project: LocalBook",
            "# @Author: Vasily Bobnev (@ardxel)",
            "# @License: MIT License",
            f"# @Date: {mtime}",
            "# @Repository: https://github.com/ardxel/localbook.git",
            "# ================================================================",
        ]
    )


def has_shebang(line: str) -> bool:
    return re.search("^#!.*/", line) is not None


def update_header(file: str):
    mtime = dt.fromtimestamp(os.path.getmtime(file))
    mtime = mtime.strftime("%d.%m.%Y %H:%M")

    with open(file, "r", encoding="utf-8") as f:
        mega_code = f.readlines()

    border_size = 2
    border_count = 0
    updated_mega_code: list[str] = []
    shebang = ""
    for i, line in enumerate(mega_code):
        # ignore shebang
        if i == 0 and has_shebang(line):
            shebang = line
            continue

        # ignore padding between shebang and possible header
        if i == 1 and not line.strip(" "):
            continue

        # ignore two borders
        borderm = re.match(r"^#\s*=+", line)
        if borderm is not None and border_count < border_size:
            border_count += 1
            continue

        # ignore header paragraph
        paragraphm = re.match(r"^#\s@\w+:\s+.*", line)
        if paragraphm is not None:
            continue

        updated_mega_code.append(line)

    result = header(mtime) + "\n" + "".join(updated_mega_code)
    if shebang:
        result = shebang + "\n" + result
    with open(file, "w", encoding="utf-8") as f:
        f.write(result)


def update_header_recursive(root: str):
    for file in glob.glob(root + "/**/*.py", recursive=True):
        print(file)
        update_header(file)


def main() -> None:
    root = git_root()
    dirs = [
        os.path.join(root, "localbook"),
        os.path.join(root, "scripts"),
        os.path.join(root, "tests"),
    ]
    mainpy = os.path.join(root, "main.py")
    update_header(mainpy)

    for dir in dirs:
        update_header_recursive(dir)


if __name__ == "__main__":
    main()
