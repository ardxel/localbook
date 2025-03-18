# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 17:29
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "pdf2image",
# ]
# ///

import glob
import os

from _config import git_root
from pdf2image import convert_from_path

ROOT = git_root()
STATIC = os.path.join(ROOT, "static")
DATA = os.path.join(STATIC, "books")
IMAGES = os.path.join(STATIC, "img")


def main() -> None:
    books = DATA
    if os.path.islink(DATA):
        books = os.readlink(DATA)

    for file in glob.glob(books + "/**/*.pdf", recursive=True):
        convert_from_path(
            pdf_path=file,
            dpi=200,
            output_folder=IMAGES,
            first_page=1,
            last_page=1,
        )
    print("Convert process complete successfully")


if __name__ == "__main__":
    main()
