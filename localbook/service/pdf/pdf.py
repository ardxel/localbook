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
from localbook.exceptions.exceptions import (
    NotFountException,
    UnsupportedMediaTypeException,
)
from localbook.lib.filesystem.pdf import is_pdf
from localbook.templates import TemplateMap


class PDFImageService:
    def __init__(self, deps: Deps = Deps()) -> None:
        self.fstree = deps.get_fstree()
        self.setting = deps.get_settings()


class PDFService:
    def __init__(self, deps: Deps = Deps()) -> None:
        self.tmpl = deps.get_tmpl()
        self.settings = deps.get_settings()
        self.fstree = deps.get_fstree()
        self.tmplmap = TemplateMap()
        self.logger = getLogger("localbook")

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
            name=self.tmplmap.pdfviewer,
            context={
                "pdf_file": pdf_file,
                "pdf_worker": pdf_worker,
                "pdf_sandbox": pdf_sandbox,
            },
        )


def get_pdf_service():
    return PDFService()
