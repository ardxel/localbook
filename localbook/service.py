# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 14:48
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
from logging import getLogger

from fastapi.requests import Request

from localbook.dependencies import Deps
from localbook.lib.filesystem.dir import is_fsdir
from localbook.lib.filesystem.pdf import is_pdf
from localbook.templates import LBTmplMap

from .exceptions.exceptions import (
    BadRequestExpection,
    NotFountException,
    UnsupportedMediaTypeException,
)


class LBLibraryService:
    def __init__(self) -> None:
        deps = Deps()
        self.tmpl = deps.get_tmpl()
        self.settings = deps.get_settings()
        self.fstree = deps.get_fstree()
        self.tmplmap = LBTmplMap()
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
            name=self.tmplmap.pages.serve_tree_view,
            context={
                "entries": entries,
                "parent_dir": dir.parent,
                "view_type": "tree",
                "toggle_view_url": toggle_view_url,
            },
        )

    async def serve_list_view(self, request: Request):
        iter_all_files = self.fstree.iter_children(recursive=True)
        pdf_files = sorted(
            (node for node in iter_all_files if is_pdf(node)),
            key=lambda pdf: pdf.name,
        )
        toggle_view_url = request.url_for("serve_tree_view", path="")
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.pages.serve_list_view,
            context={
                "pdf_files": pdf_files,
                "view_type": "list",
                "toggle_view_url": toggle_view_url,
            },
        )

    async def serve_pdf(self, request: Request, path: str):
        """use pdfjs library to render pdf documents"""
        pdf_node = self.fstree.get_node(path)
        if not pdf_node:
            raise NotFountException(f"Error: PDF file '{path}' not found")
        elif not is_pdf(pdf_node):
            # TODO: implement better error handling in this block
            raise UnsupportedMediaTypeException(pdf_node)

        # TODO: implement autoload dependencies
        pdfjs_package = "static/packages/pdfjs"
        if not os.path.exists(pdfjs_package):
            self.logger.error(
                "pdfjs module is not exists. Update dependencies by script"
            )

        pdf_file = request.url_for("static", path=os.path.join("books", path))
        pdf_worker = request.url_for(
            "static", path="packages/pdfjs/build/pdf.worker.mjs"
        )
        pdf_sandbox = request.url_for(
            "static", path="packages/pdfjs/build/pdf.sandbox.mjs"
        )
        return self.tmpl.TemplateResponse(
            request=request,
            name=self.tmplmap.pages.pdfviewer,
            context={
                "pdf_file": pdf_file,
                "pdf_worker": pdf_worker,
                "pdf_sandbox": pdf_sandbox,
            },
        )
