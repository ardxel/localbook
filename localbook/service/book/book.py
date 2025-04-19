# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
from logging import getLogger
from typing import Optional

from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from localbook.dependencies import get_fstree, get_jinja2
from localbook.exceptions.exceptions import (
    NotFountException,
    UnsupportedMediaTypeException,
)
from localbook.lib.filesystem.pdf import is_pdf
from localbook.lib.filesystem.tree import FSTree
from localbook.templates import TemplateMap


class BookService:
    def __init__(
        self,
        jinja2: Optional[Jinja2Templates] = None,
        fstree: Optional[FSTree] = None,
        tmpl_map: Optional[TemplateMap] = None,
    ) -> None:
        self.jinja2 = jinja2 or get_jinja2()
        self.fstree = fstree or get_fstree()
        self.tmplmap = tmpl_map or TemplateMap()
        self.logger = getLogger("localbook")

    async def serve_book(self, request: Request, path: str):
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
        return self.jinja2.TemplateResponse(
            request=request,
            name=self.tmplmap.pdfviewer,
            context={
                "pdf_file": pdf_file,
                "pdf_worker": pdf_worker,
                "pdf_sandbox": pdf_sandbox,
            },
        )


def get_book_service():
    return BookService()
