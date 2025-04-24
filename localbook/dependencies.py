# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import logging
import sys
from warnings import deprecated

from fastapi.templating import Jinja2Templates

from localbook.config import FSSettings, ServerSettings, Settings
from localbook.lib.decorators import singleton
from localbook.lib.filesystem.tree import FSTree


class _AppLogger:
    __established = False

    def __init__(self, settings: ServerSettings) -> None:
        self.settings = settings

    def setup(self):
        if self.__established:
            return

        self.__setup_main_logger()
        self.__setup_debug_logger()
        self.__established = True

    def __setup_main_logger(self):
        self.settings
        logger = logging.getLogger("localbook")
        match self.settings.mode:
            case "development":
                logger.setLevel(logging.ERROR)
            case "production":
                logger.setLevel(logging.WARNING)
        logger.exception
        if not logger.hasHandlers():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logger.getEffectiveLevel())
            formatter = logging.Formatter(
                "%(asctime)s %(name)s %(levelname)s : %(message)s",
                "%d.%m.%y %H:%M:%S",
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    def __setup_debug_logger(self):
        logger = logging.getLogger("localbook.debug")
        log_level = logging.NOTSET
        if self.settings.debug:
            log_level = logging.DEBUG

        logger.setLevel(log_level)
        if not logger.hasHandlers():
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logger.getEffectiveLevel())
            formatter = logging.Formatter(
                "%(levelname)s : %(message)s",
                "%d.%m.%y %H:%M:%S",
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)


@singleton
class Deps:
    def __init__(self) -> None:
        self.__settings = Settings()
        appLogger = _AppLogger(self.server_settings)
        appLogger.setup()
        self.__tmpl = Jinja2Templates(directory="templates")
        self.__fstree = FSTree(
            root=self.__settings.filesystem.user_data_location,
            max_depth=self.__settings.filesystem.dfs_max_depth,
            follow_symlink=True,
            normalize=True,
        )

    @property
    def settings(self) -> Settings:
        return self.__settings

    @property
    def server_settings(self) -> ServerSettings:
        return self.__settings.server

    @property
    def fs_settings(self) -> FSSettings:
        return self.__settings.filesystem

    @property
    def jinja2(self) -> Jinja2Templates:
        return self.__tmpl

    @property
    def fstree(self) -> FSTree:
        return self.__fstree

    @deprecated("get_settings is deprecated. Use `settings` instead")
    def get_settings(self) -> Settings:
        return self.settings

    @deprecated("get_fstree is deprecated. Use `fstree` property instead")
    def get_fstree(self) -> FSTree:
        return self.fstree

    @deprecated("get_tmpl is deprecated. Use `jinja2` property instead")
    def get_tmpl(self) -> Jinja2Templates:
        return self.jinja2


def get_settings() -> Settings:
    return Deps().settings


def get_server_settings() -> ServerSettings:
    return Deps().server_settings


def get_fs_settings() -> FSSettings:
    return Deps().fs_settings


def get_fstree() -> FSTree:
    return Deps().fstree


def get_jinja2() -> Jinja2Templates:
    return Deps().jinja2
