# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 17.03.2025 11:14
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from localbook.core.filesystem.nodes import is_fsdir, is_fsfile, is_pdf
from localbook.dependencies import Deps
from localbook.exceptions.exceptions import (
    NotFountException,
    UnsupportedMediaTypeException,
)
from localbook.templates import LBTmplMap

router = APIRouter()
tmpl = Deps().get_tmpl()
fstree = Deps().get_fstree()
tmplmap = LBTmplMap()


@router.get("/books/tree/{path:path}", response_class=HTMLResponse)
async def serve_tree_view(request: Request, path=""):
    dir = fstree.get_node(path)
    if dir is None and path == "":
        dir = fstree.get_root_node()
    if dir is None:
        raise NotFountException(f"Error: file '{path}' not found")
    if not is_fsdir(dir):
        raise UnsupportedMediaTypeException(dir)
    pdfs, others, directories = [], [], []
    for node in sorted(dir.iter_children(), key=lambda n: n.name):
        if node.isdir():
            directories.append(node)
        elif is_fsfile(node):
            match node.mime:
                case "application/pdf":
                    pdfs.append(node)
                case _:
                    others.append(node)
    go_back_link = dir.parent.relpath if dir.parent is not None else None
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.serve_tree_view,
        context={
            "others": others,
            "directories": directories,
            "pdfs": pdfs,
            "go_back_link": go_back_link,
        },
    )


@router.get("/books/list", response_class=HTMLResponse)
async def serve_list_view(request: Request):
    pdfs = sorted(
        (node for node in fstree.iter_children(recursive=True) if is_pdf(node)),
        key=lambda pdf: pdf.name,
    )
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.serve_list_view,
        context={"pdfs": pdfs},
    )


@router.get("/books/pdf-view/{path:path}", response_class=HTMLResponse)
async def serve_pdf(request: Request, path=""):
    return tmpl.TemplateResponse(
        request=request,
        name=tmplmap.pages.pdfviewer,
        context={
            "pdf_path": os.path.join("books", path),
        },
    )
