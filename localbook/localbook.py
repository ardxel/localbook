# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from localbook.controller.library import router as library_router
from localbook.dependencies import Deps
from localbook.exceptions.handlers import ExceptionRender
from localbook.service.book.cover import BookCoverGenerator


class LocalBook:
    def __init__(self) -> None:
        self.app = FastAPI()
        self._dependencies = Deps()
        self.cors()
        self.static()
        self.configure_exceptions()
        self.configure_routes()

    def cors(self):
        """CORS"""
        port = self._dependencies.settings.server.port
        origins = [
            f"http://localhost:{port}",
            f"http://0.0.0.0:{port}",
            f"http://127.0.0.1:{port}",
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def static(self):
        """STATIC"""
        pdf_cover_generator = BookCoverGenerator()
        pdf_cover_generator.generate()

        self.app.mount(
            "/build/images",
            StaticFiles(directory="build/images", follow_symlink=False),
            name="build/images",
        )

        self.app.mount(
            "/static",
            StaticFiles(directory="static", follow_symlink=True),
            name="static",
        )

    def configure_exceptions(self):
        """EXCEPTIONS"""
        exc_render = ExceptionRender(self.app)
        exc_render.configure()

    def configure_routes(self):
        """ROUTING"""
        self.app.include_router(library_router)
