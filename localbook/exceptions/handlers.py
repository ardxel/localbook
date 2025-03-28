# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 26.03.2025 10:53
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import HTTPException, Request

from localbook.dependencies import Deps
from localbook.templates import TemplateMap

from .exceptions import BadRequestExpection, UnsupportedMediaTypeException

tmpl = Deps().get_tmpl()
tmplmap = TemplateMap()


async def not_found_handler(request: Request, exc: HTTPException):
    return tmpl.TemplateResponse(
        request,
        name=tmplmap.err404,
    )


async def unsupported_media_type_handler(
    request: Request,
    exc: UnsupportedMediaTypeException,
):
    return tmpl.TemplateResponse(
        request,
        name=tmplmap.err415,
        context={"bad_mime": exc.mime or "unknown"},
    )


async def bad_request_handler(request: Request, exc: BadRequestExpection):
    # TODO: create specific template for handling bad request error
    return tmpl.TemplateResponse(
        request,
        name=tmplmap.err404,
    )
