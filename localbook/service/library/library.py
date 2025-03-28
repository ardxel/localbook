# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 14:48
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from logging import getLogger

from fastapi.requests import Request

from localbook.dependencies import Deps
from localbook.exceptions.exceptions import BadRequestExpection, NotFountException
from localbook.lib.filesystem.dir import is_fsdir
from localbook.lib.filesystem.pdf import is_pdf
from localbook.templates import TemplateMap


class LibraryService:
    def __init__(
        self,
        deps: Deps = Deps(),
    ) -> None:
        self.fstree = deps.get_fstree()
        self.tmpl = deps.get_tmpl()
        self.settings = deps.get_settings()
        self.fstree = deps.get_fstree()
        self.tmplmap = TemplateMap()
        self.logger = getLogger("localbook")

    async def serve_tree_view(self, request: Request, path=""):
        dir = self.fstree.get_node(path)
        if dir is None and path == "":
            dir = self.fstree.get_root_node()
        if dir is None:
            raise NotFountException(f"Error: directory '{path}' not found")
        if not is_fsdir(dir):
            raise BadRequestExpection(f"Error: {path} is not a directory")

        entries = sorted(dir.iter_children(), key=lambda n: n.name)
        toggle_view_url = request.url_for("serve_list_view")
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.serve_tree_view,
            context={
                "entries": entries,
                "parent_dir": dir.parent,
                "view_type": "tree",
                "toggle_view_url": toggle_view_url,
            },
        )

    async def serve_list_view(self, request: Request):
        pdf_files = self.fstree.pdf_list()
        pdf_files = sorted(pdf_files, key=lambda x: x.name)
        toggle_view_url = request.url_for("serve_tree_view", path="")
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.serve_list_view,
            context={
                "pdf_files": pdf_files,
                "view_type": "list",
                "toggle_view_url": toggle_view_url,
            },
        )


def get_lib_service():
    return LibraryService()
