# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import os
import shutil
from abc import abstractmethod
from io import BytesIO
from logging import getLogger
from typing import Optional
from urllib.parse import urljoin
from zipfile import ZipFile

import requests
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from localbook.config import (
    CACHE_PJDFJS_PACKAGE_DIR,
    PDFJS_SOURCE_URL,
    PDFJS_VERSION_FILE,
)
from localbook.dependencies import get_fstree, get_jinja2
from localbook.exceptions.exceptions import (
    NotFoundException,
    UnsupportedMediaTypeException,
)
from localbook.lib.filesystem.pdf import PDFFile, is_pdf
from localbook.lib.filesystem.tree import FSTree
from localbook.lib.static import StaticComponent
from localbook.templates import TemplateMap


class MozillaViewerPackage:
    def __init__(
        self,
        version_file: Optional[str] = None,
        package_dir: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> None:
        self._version_file = version_file or PDFJS_VERSION_FILE
        self.__version = self.__read_version()
        self.__loaded = False
        self.data_dir = package_dir or CACHE_PJDFJS_PACKAGE_DIR
        self.source_url = source_url or urljoin(
            PDFJS_SOURCE_URL, f"v{self.__version}/{self.remote_package_name}"
        )

    @property
    def version(self) -> str:
        return self.__version

    @property
    def remote_package_name(self) -> str:
        return f"pdfjs-{self.version}-dist.zip"

    @property
    def loaded(self) -> bool:
        return self.__loaded

    def __read_version(self) -> str:
        """returns pdfjs version"""
        with open(self._version_file, "r") as f:
            version = f.read().strip()
            return version

    def download(self, cache: bool = True, extract_to: str = ""):
        """download pdfjs package"""
        extract_to = extract_to or self.data_dir
        if os.path.exists(extract_to):
            self.__loaded = True
            if cache:  # skip download stage
                return
            shutil.rmtree(extract_to)

        try:
            response = requests.get(self.source_url)
            response.raise_for_status()
            buffer = BytesIO(response.content)
            with ZipFile(buffer) as zf:
                zf.extractall(extract_to)
        except Exception as e:
            raise e

        self.__loaded = True


class MozillaViewerPackageStaticComponent(StaticComponent):
    def __init__(self, static_path: str) -> None:
        super().__init__(static_path)

    def mount(self, app: FastAPI) -> None:
        package = MozillaViewerPackage()
        if not package.loaded:
            package.download(cache=True)

        app.mount(
            self.static_path,
            StaticFiles(directory=package.data_dir),
            name=self.static_path,
        )


class BookViewer:
    def __init__(
        self,
        template_name: Optional[str] = None,
        jinja2: Optional[Jinja2Templates] = None,
    ) -> None:
        self.jinja2 = jinja2
        self.template_name = template_name

    @abstractmethod
    def render(self, request: Request, book: PDFFile) -> _TemplateResponse:
        pass


class BookViewerMozilla(BookViewer):
    def __init__(
        self,
        template_name: Optional[str] = None,
        jinja2: Optional[Jinja2Templates] = None,
        **kwargs,
    ) -> None:
        self.template_name = template_name or TemplateMap().book_viewer_mozilla
        self.jinja2 = jinja2 or get_jinja2()
        self.mozilla_pkg: MozillaViewerPackage = (
            kwargs.get("mozilla_package") or MozillaViewerPackage()
        )

    def render(self, request: Request, book: PDFFile) -> _TemplateResponse:
        pdf_worker = request.url_for(
            "/build/packages/pdfjs", path="build/pdf.worker.mjs"
        )
        pdf_sandbox = request.url_for(
            "/build/packages/pdfjs", path="build/pdf.sandbox.mjs"
        )
        pdf_file = request.url_for("/build/books", path=book.relpath)

        return self.jinja2.TemplateResponse(
            request=request,
            name=self.template_name,
            context={
                "pdf_file": pdf_file,
                "pdf_worker": pdf_worker,
                "pdf_sandbox": pdf_sandbox,
            },
        )


class BookViewerNative(BookViewer):
    pass


class BookService:
    def __init__(
        self,
        jinja2: Optional[Jinja2Templates] = None,
        fstree: Optional[FSTree] = None,
        tmpl_map: Optional[TemplateMap] = None,
        book_viewer: Optional[BookViewer] = None,
    ) -> None:
        self.jinja2 = jinja2 or get_jinja2()
        self.fstree = fstree or get_fstree()
        self.tmplmap = tmpl_map or TemplateMap()
        self.book_viewer = book_viewer or BookViewerMozilla()
        self.logger = getLogger("localbook")

    async def serve_book(self, request: Request, path: str):
        """Render book"""
        book_node = self.fstree.get_node(path)
        if not book_node:
            raise NotFoundException(f"Error: PDF file '{path}' not found.")

        if is_pdf(book_node) and isinstance(book_node, PDFFile):
            return self.book_viewer.render(request, book_node)
        else:
            raise UnsupportedMediaTypeException()


def get_book_service():
    return BookService()
