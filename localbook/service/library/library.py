# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from logging import getLogger
from typing import Optional

from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from localbook.config import Settings
from localbook.dependencies import get_fstree, get_jinja2, get_settings
from localbook.exceptions.exceptions import BadRequestExpection, NotFoundException
from localbook.lib.filesystem.dir import FSDir, is_fsdir
from localbook.lib.filesystem.pdf import PDFFile, is_pdf
from localbook.lib.filesystem.tree import FSTree
from localbook.service.book.cover import BookCoverService
from localbook.templates import TemplateMap


class LibraryServiceContextBuilder:
    def __init__(
        self,
        fstree: Optional[FSTree] = None,
        pdf_cover_service: Optional[BookCoverService] = None,
    ) -> None:
        self.fstree = fstree or get_fstree()
        self.pdf_cover_service = pdf_cover_service or BookCoverService()

    def build_tree_view(self, request: Request, root: FSDir):
        entries = sorted(root.iter_children(), key=lambda n: n.name)
        toggle_view_url = request.url_for("serve_list_view")
        breadcrumbs = root.relpath and "/" + root.relpath or "/"
        context = {
            "entries": entries,
            "parent_dir": root.parent,
            "view_type": "tree",
            "toggle_view_url": toggle_view_url,
            "breadcrumbs": breadcrumbs,
        }
        return context

    def normalize_cover_file(self, f: str, nid: str) -> str:
        relpath = f[f.index(nid) :]
        prefix = "/build/images/covers"
        return f"{prefix}/{relpath}"

    def build_list_view(self, request: Request):
        pdf_files = sorted(self.fstree.pdf_list(), key=lambda x: x.name)
        covers: dict[str, str] = {}
        for pdf in pdf_files:
            if is_pdf(pdf) and isinstance(pdf, PDFFile):
                cover_file = self.pdf_cover_service.get_cover(pdf)
                cover_file = self.normalize_cover_file(cover_file, pdf.nid)
                covers[pdf.nid] = cover_file
        toggle_view_url = request.url_for("serve_tree_view", path="")
        context = {
            "pdf_files": pdf_files,
            "covers": covers,
            "view_type": "list",
            "toggle_view_url": toggle_view_url,
        }
        return context


class LibraryService:
    def __init__(
        self,
        pdf_cover_service: Optional[BookCoverService] = None,
        ctx_builder: Optional[LibraryServiceContextBuilder] = None,
        settings: Optional[Settings] = None,
        fstree: Optional[FSTree] = None,
        jinja2: Optional[Jinja2Templates] = None,
        tmplmap: Optional[TemplateMap] = None,
    ) -> None:
        self.logger = getLogger("localbook")
        self.fstree = fstree or get_fstree()
        self.tmpl = jinja2 or get_jinja2()
        self.settings = settings or get_settings()
        self.tmplmap = tmplmap or TemplateMap()
        self.pdf_cover_service = pdf_cover_service or BookCoverService()
        self.ctx_builder = ctx_builder or LibraryServiceContextBuilder()

    async def serve_tree_view(self, request: Request, path=""):
        if path == "":  # default value
            dir = self.fstree.get_root_node()
        else:
            dir = self.fstree.get_node(path)
        if dir is None:
            raise NotFoundException(f"Error: directory '{path}' not found")
        if not is_fsdir(dir):
            raise BadRequestExpection(f"Error: {path} is not a directory")

        context = self.ctx_builder.build_tree_view(request, root=dir)
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.serve_tree_view,
            context=context,
        )

    async def serve_list_view(self, request: Request):
        context = self.ctx_builder.build_list_view(request)
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.serve_list_view,
            context=context,
        )


def get_lib_service():
    return LibraryService()
