# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 17.03.2025 11:14
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


import logging
import os

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from localbook.dependencies import Deps
from localbook.exceptions.exceptions import (
    BadRequestExpection,
    NotFountException,
    UnsupportedMediaTypeException,
)
from localbook.lib.filesystem.nodes import is_fsdir, is_fsfile, is_pdf
from localbook.templates import LBTmplMap

router = APIRouter(prefix="/library")
dependencies = Deps()
tmpl = dependencies.get_tmpl()
fstree = dependencies.get_fstree()
logger = logging.getLogger("localbook")
tmplmap = LBTmplMap()


@router.get("/tree/{path:path}", response_class=HTMLResponse)
async def serve_tree_view(request: Request, path=""):
    dir = fstree.get_node(path)
    if dir is None and path == "":
        dir = fstree.get_root_node()
    if dir is None:
        raise NotFountException(f"Error: directory '{path}' not found")
    if not is_fsdir(dir):
        raise BadRequestExpection(f"Error: {path} is not a directory")

    entries = sorted(dir.iter_children(), key=lambda n: n.name)
    toggle_view_url = request.url_for("serve_list_view")
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.serve_tree_view,
        context={
            "entries": entries,
            "parent_dir": dir.parent,
            "view_type": "tree",
            "toggle_view_url": toggle_view_url,
        },
    )


@router.get("/list", response_class=HTMLResponse)
async def serve_list_view(request: Request):
    pdf_files = sorted(
        (node for node in fstree.iter_children(recursive=True) if is_pdf(node)),
        key=lambda pdf: pdf.name,
    )
    toggle_view_url = request.url_for("serve_tree_view", path="")
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.serve_list_view,
        context={
            "pdf_files": pdf_files,
            "view_type": "list",
            "toggle_view_url": toggle_view_url,
        },
    )


@router.get("/pdf-view/{path:path}", response_class=HTMLResponse)
async def serve_pdf(request: Request, path: str):
    """use pdfjs library to render pdf documents"""
    pdf_node = fstree.get_node(path)
    if not pdf_node:
        raise NotFountException(f"Error: PDF file '{path}' not found")
    elif not is_pdf(pdf_node):
        # TODO: implement better error handling in this block
        raise UnsupportedMediaTypeException(pdf_node)

    # TODO: implement autoload dependencies
    pdfjs_package = "static/packages/pdfjs"
    if not os.path.exists(pdfjs_package):
        logger.error("pdfjs module is not exists. Update dependencies by script")

    pdf_file = request.url_for("static", path=os.path.join("books", path))
    pdf_worker = request.url_for("static", path="packages/pdfjs/build/pdf.worker.mjs")
    pdf_sandbox = request.url_for("static", path="packages/pdfjs/build/pdf.sandbox.mjs")
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.pdfviewer,
        context={
            "pdf_file": pdf_file,
            "pdf_worker": pdf_worker,
            "pdf_sandbox": pdf_sandbox,
        },
    )
