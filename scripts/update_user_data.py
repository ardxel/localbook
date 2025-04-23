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

import os
import shutil
import sys

import _config

ROOT = _config.git_root()
STATIC = os.path.join(ROOT, "static")
DATA = os.path.join(STATIC, "books")
IMAGES = os.path.join(STATIC, "jpeg")

system_cfg, server_cfg = _config.config()
extend_data = bool(system_cfg["extend_data"])
user_data_location: str = system_cfg["user_data_location"]
if user_data_location.startswith("~"):
    user_data_location = os.path.abspath(os.path.expanduser(user_data_location))


def create_symlink() -> None:
    if not os.path.isdir(user_data_location):
        print("Error: user source path is not a directory")
        sys.exit(1)

    if os.path.islink(DATA):
        old_src = os.readlink(DATA)
        if old_src == user_data_location:
            print("Symlink is already exist")
            return

    os.symlink(user_data_location, DATA, True)
    print("Symlink created")


def recursive_copy() -> None:
    shutil.copytree(user_data_location, DATA, dirs_exist_ok=True)


def main() -> None:
    if not os.path.isdir(IMAGES):
        os.mkdir(IMAGES)
    if extend_data:
        recursive_copy()
    else:
        create_symlink()


if __name__ == "__main__":
    main()
