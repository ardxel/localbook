# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
import subprocess
import sys
import tomllib
from typing import Any


def git_root() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Not inside a Git repository.")
        sys.exit(1)


def config() -> tuple[dict[str, Any], dict[str, Any]]:
    """return tuple (system,server) config parsed from \"config.toml\" """
    root = git_root()
    with open(os.path.join(root, "config.toml"), "rb") as bfile:
        cfg = tomllib.load(bfile)
    cfg_system = cfg["system"]
    cfg_server = cfg["server"]
    return cfg_system, cfg_server
