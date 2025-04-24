# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
import shutil
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from localbook.lib.decorators import singleton

DATA_LOCATION = "build/books"


class ServerSettings(BaseModel):
    port: int = 3102
    host: str = "localhost"
    debug: bool = False
    mode: str = "development"


class FSSettings(BaseModel):
    user_data_location: str
    extend_data: bool = False  # force copy user data to static/books
    dfs_max_depth: int = 3

    def _validate_user_loc(self, loc: str):
        if not os.path.exists(loc):
            raise ValueError(
                f"Error: user data location is not a directory.\nGot user path: {loc}"
            )

        loc = os.path.realpath(loc)
        if not os.path.exists(loc):
            raise ValueError(
                f"Error: user data location is not exists.\nGot real path: {loc}"
            )

        if not os.path.isdir(loc):
            raise ValueError(
                f"Error: user data location must be a directory.\nGot: {loc}"
            )

    def model_post_init(self, __context):
        try:
            # validate config.filesystem.user_data_location
            self._validate_user_loc(self.user_data_location)
        except ValueError as e:
            raise e

        books_loc = os.path.relpath(DATA_LOCATION)

        # clear existed data
        if os.path.exists(books_loc):
            shutil.rmtree(books_loc)

        if os.path.islink(self.user_data_location):
            # read symlink
            self.user_data_location = os.path.realpath(self.user_data_location)
        if self.extend_data:
            # copy data folder recursively
            shutil.copytree(self.user_data_location, books_loc, dirs_exist_ok=True)
        else:
            # create symlink
            os.symlink(self.user_data_location, books_loc, True)

        if self.dfs_max_depth < 1:
            self.dfs_max_depth = 1


@singleton
class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")
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
        return (TomlConfigSettingsSource(settings_cls),)
