# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 24.04.2025 16:20
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///

import os

from _config import get_toml_config, git_root

ROOT = git_root()
ENV_PREVIX = "APP_"
ENV_FILESYSTEM_PREFIX = "FILESYSTEM__"
ENV_SERVER_PREFIX = "SERVER__"
ENV_FILE = ".docker/.env"


def toml_to_env():
    env_file = os.path.join(ROOT, ENV_FILE)
    cfg_fs, cfg_server = get_toml_config()

    with open(env_file, "w", encoding="utf-8") as f:
        for k in cfg_fs:
            key = f"{ENV_PREVIX}{ENV_FILESYSTEM_PREFIX}{k.upper()}"
            val = str(cfg_fs[k])
            f.write(f"{key}={val}\n")
        for k in cfg_server:
            key = f"{ENV_PREVIX}{ENV_SERVER_PREFIX}{k.upper()}"
            val = str(cfg_server[k])
            f.write(f"{key}={val}\n")


toml_to_env()
