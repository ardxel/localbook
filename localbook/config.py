# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 07:37
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os
import sys
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from localbook.core.decorators import singleton


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
        """validate 'user_data_location'"""
        if not self.extend_data:
            books_loc = os.path.abspath("static/books")
            if os.path.islink(books_loc):
                sl = os.readlink(books_loc)
                if not os.path.isdir(sl):
                    print("Error: user data location must be a directory")
                    print(f"Got user path: {sl}")
                    sys.exit(1)
                self.user_data_location = sl

            else:
                print("Error: static/books must be a symlink")
                sys.exit(1)

        """validate 'dfs_max_depth'"""
        if self.dfs_max_depth < 1:
            self.dfs_max_depth = 1


@singleton
class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")
    server: ServerSettings
    system: FSSettings

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
