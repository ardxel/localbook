# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.03.2025 17:56
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import logging
import sys

from fastapi.templating import Jinja2Templates

from localbook.config import Settings
from localbook.lib.decorators import singleton
from localbook.lib.filesystem.tree import FSTree


@singleton
class Deps:
    def __init__(self) -> None:
        self.settings = Settings()
        self._init_logger()
        self.tmpl = Jinja2Templates(directory="templates")
        self.fstree = FSTree(
            root=self.settings.system.user_data_location,
            max_depth=self.settings.system.dfs_max_depth,
        )

    def _init_logger(self):
        server_settings = self.get_settings().server
        debug = server_settings.debug
        prod = server_settings.mode == "production"
        logger = logging.getLogger("localbook")
        if prod:
            log_level = logging.WARNING
        elif debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        logger.setLevel(log_level)
        if not logger.hasHandlers():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s : %(message)s",
                "%d.%m.%y %H:%M:%S",
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    def get_settings(self) -> Settings:
        return self.settings

    def get_fstree(self) -> FSTree:
        return self.fstree

    def get_tmpl(self) -> Jinja2Templates:
        return self.tmpl
