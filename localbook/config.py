# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
import shutil
from typing import Optional, Tuple, Type

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from localbook.lib.decorators import singleton
from localbook.lib.static import StaticComponent

CACHE_DEFAULT_ROOT = ".cache"
CACHE_BOOKS_LOCATION = ".cache/books"
CACHE_BOOK_COVER_DIR = ".cache/images/book/covers"
CACHE_COVER_METADATA_FILE = ".cache/metadata/book/covers.json"

CACHE_NPM_PACKAGES_DIR = ".cache/packages"
CACHE_PJDFJS_PACKAGE_DIR = ".cache/packages/pdfjs"
PDFJS_VERSION_FILE = ".pdfjs-version"
PDFJS_SOURCE_URL = "https://github.com/mozilla/pdf.js/releases/download/"

CONFIG_TOML = "config.toml"
ENV_PREFIX = "APP_"


class ServerSettings(BaseModel):
    port: int = 3102
    host: str = "localhost"
    debug: bool = False
    mode: str = "development"


class FSSettings(BaseModel):
    user_data_location: str
    extend_data: bool = False  # force copy user data to static/books
    dfs_max_depth: int = 3

    def model_post_init(self, __context):
        build_dir = os.path.relpath(CACHE_DEFAULT_ROOT)
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)

        if self.dfs_max_depth < 1:
            self.dfs_max_depth = 1


@singleton
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=CONFIG_TOML,
        env_prefix=ENV_PREFIX,
        env_nested_delimiter="__",
    )
    server: ServerSettings
    filesystem: FSSettings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        env_keys = os.environ.keys()
        has_env_keys = any(k.startswith(ENV_PREFIX) for k in env_keys)
        if has_env_keys:
            return (env_settings,)
        else:
            return (TomlConfigSettingsSource(settings_cls),)


class UBooksConfigurator:
    def __init__(
        self,
        books_location: Optional[str] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self.settings = settings or Settings()
        self.data_dir = books_location or CACHE_BOOKS_LOCATION
        self.user_location = self._normalize_user_location(
            self.settings.filesystem.user_data_location
        )
        self.extend_data = self.settings.filesystem.extend_data
        self.__configured = False

    def _normalize_user_location(self, path: str) -> str:
        # fmt: off
        assert os.path.exists(path), f"Error: user data location is not a directory. Got user path: {path}"
        if os.path.islink(path):
            path = os.path.realpath(path)
        assert os.path.isdir(path), f"Error: user data location must be a directory.\nGot: {path}"
        return path
        # fmt: on

    def configure(self, cache=True) -> None:

        # clear existed data
        if os.path.exists(self.data_dir):
            if os.path.islink(self.data_dir):
                os.remove(self.data_dir)
            else:
                if cache:  # skip
                    self.__configured = True
                    return
                shutil.rmtree(self.data_dir)

        if self.extend_data:
            # copy data folder recursively
            shutil.copytree(
                src=self.user_location,
                dst=self.data_dir,
                dirs_exist_ok=True,
            )
        else:
            # create symlink
            os.symlink(self.user_location, self.data_dir, True)


class UBookStaticComponent(StaticComponent):
    def __init__(self, static_path: str) -> None:
        super().__init__(static_path)

    def mount(self, app: FastAPI) -> None:
        configurator = UBooksConfigurator()
        configurator.configure(cache=True)

        app.mount(
            self.static_path,
            StaticFiles(directory=configurator.data_dir),
            self.static_path,
        )
