# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 14:56
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from localbook.service import LBLibraryService


class LibraryRouter:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/library")
        self.library_service = LBLibraryService()

        self.router.add_api_route(
            "/tree/{path:path}",
            name="serve_tree_view",
            methods=["GET"],
            endpoint=self.library_service.serve_tree_view,
            response_class=HTMLResponse,
        )

        self.router.add_api_route(
            "/list",
            name="serve_list_view",
            methods=["GET"],
            endpoint=self.library_service.serve_list_view,
            response_class=HTMLResponse,
        )

        self.router.add_api_route(
            "/pdf-view/{path:path}",
            name="serve_pdf",
            methods=["GET"],
            endpoint=self.library_service.serve_pdf,
            response_class=HTMLResponse,
        )

    def get_router(self) -> APIRouter:
        return self.router
