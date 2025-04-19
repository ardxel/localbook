# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from localbook.service.book import BookService, get_book_service
from localbook.service.library import LibraryService, get_lib_service

router = APIRouter(prefix="/library")


@router.get("/tree/{path:path}", response_class=HTMLResponse)
async def serve_tree_view(
    service: Annotated[LibraryService, Depends(get_lib_service)],
    request: Request,
    path: str = "",
):
    return await service.serve_tree_view(request, path)


@router.get("/list", response_class=HTMLResponse)
async def serve_list_view(
    service: Annotated[LibraryService, Depends(get_lib_service)],
    request: Request,
):
    return await service.serve_list_view(request)


@router.get("/book/{path:path}", response_class=HTMLResponse)
async def serve_book(
    service: Annotated[BookService, Depends(get_book_service)],
    request: Request,
    path: str,
):
    return await service.serve_book(request, path)
