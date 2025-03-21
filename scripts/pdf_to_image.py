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
import hashlib
import os
import shutil
import sys

from _config import git_root
from pdf2image import convert_from_path
from PIL.Image import Image, Resampling


def hash_path(path: str) -> str:
    """generate inique hash from absolute file path."""
    if not os.path.isabs(path):
        raise ValueError(f'Error: path "{path}"  is not absolute.')
    return hashlib.md5(path.encode()).hexdigest()


class ImageSettings:
    def __init__(self, dpi: int, quality: int, page_x: int, page_y: int) -> None:
        self._format = "JPEG"
        self.dpi = dpi
        self.quality = quality
        self.page_x = page_x
        self.page_y = page_y


class PDFImageBuilder:
    def __init__(self, pdf_file: str, settings: ImageSettings) -> None:
        self.pdf_file = pdf_file
        self.settings = settings
        self._ppm: None | Image = None
        self.image: None | Image = None

    def convert_to_image(self):
        first_page_image = convert_from_path(
            pdf_path=self.pdf_file,
            dpi=self.settings.dpi,
            first_page=1,
            last_page=1,
        ).pop()

        if self._ppm is None:
            self._ppm = first_page_image
        self.image = self._ppm.resize(
            (self.settings.page_x, self.settings.page_y),
            resample=Resampling.LANCZOS,
        )

    def save(self, file_path: str):
        if self.image is None:
            print(f"Image {self.pdf_file} is not created.")
            return
        self.image.save(
            file_path,
            format=self.settings._format,
            quality=self.settings.quality,
        )


ROOT = git_root()
IMAGE_SETTINGS = {
    "desktop": ImageSettings(dpi=72, quality=85, page_x=170, page_y=250),
    "laptop": ImageSettings(dpi=72, quality=85, page_x=150, page_y=230),
    "tablet": ImageSettings(dpi=72, quality=85, page_x=140, page_y=200),
    "mobile": ImageSettings(dpi=72, quality=85, page_x=120, page_y=180),
}


def main() -> None:
    static = os.path.join(ROOT, "static")
    user_data = os.path.join(static, "books")
    pdf_images = os.path.join(static, "images/pdf")

    # chech user data
    if not os.path.exists(user_data):
        print("Error: user data is not exists.")
        print(f"Check user data dir {user_data}")
        sys.exit(1)

    shutil.rmtree(pdf_images)
    os.makedirs(pdf_images)

    if os.path.islink(user_data):
        user_data = os.readlink(user_data)

    pdf_files = glob.glob(user_data + "/**/*.pdf", recursive=True)
    for pdf_file in pdf_files:
        hfile = hash_path(os.path.abspath(pdf_file))
        hfile_path = os.path.join(pdf_images, hfile)
        os.mkdir(hfile_path)
        for device, settings in IMAGE_SETTINGS.items():
            builder = PDFImageBuilder(pdf_file, settings)
            builder.convert_to_image()
            image_file = os.path.join(hfile_path, f"{device}.jpeg")
            builder.save(image_file)

        print(f"file converted: {pdf_file}")


if __name__ == "__main__":
    main()
