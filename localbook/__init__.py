# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 07:17
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from localbook.dependencies import Deps
from localbook.exceptions import exception_handlers
from localbook.router import router


class LocalBook:
    def __init__(self) -> None:
        self.app = FastAPI()
        self._dependencies = Deps()

        self.app.add_event_handler("startup", self._check_static)
        self.cors()
        self.static()
        self.configure_exceptions()
        self.configure_routes()

    def cors(self):
        port = self._dependencies.get_settings().server.port
        origins = [
            f"http://localhost:{port}",
            f"http://0.0.0.0:{port}",
            f"http://127.0.0.1:{port}",
        ]

        """CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def static(self):
        """STATIC"""
        self.app.mount(
            "/static",
            StaticFiles(directory="static", follow_symlink=True),
            name="static",
        )

    def configure_exceptions(self):
        """EXCEPTIONS"""
        for exc_handler in exception_handlers:
            self.app.add_exception_handler(
                exc_handler.status_code,
                handler=exc_handler.handler,
            )

    def configure_routes(self):
        """ROUTING"""
        self.app.include_router(router)

    def _check_static(self):
        logger = logging.getLogger("localbook")

        if not os.path.exists("static/books"):
            logger.warning(
                "User data is not exists in static. Please use special script"
            )

        if not os.path.exists("static/books/jpeg"):
            logger.warning("PDF images is not generated. Plese use special script")

        if not os.path.exists("static/packages/pdfjs"):
            logger.warning("pdfjs module is not exists. Please use special script")
