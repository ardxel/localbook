from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from localbook.service.library import LibraryService, get_lib_service
from localbook.service.pdf import PDFService, get_pdf_service

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


@router.get("/pdf-view/{path:path}", response_class=HTMLResponse)
async def serve_pdf(
    service: Annotated[PDFService, Depends(get_pdf_service)],
    request: Request,
    path: str,
):
    return await service.serve_pdf(request, path)
