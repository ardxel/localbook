# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from fastapi import HTTPException, Request

from localbook.dependencies import Deps, get_jinja2
from localbook.templates import TemplateMap

from .exceptions import BadRequestExpection, UnsupportedMediaTypeException

tmplmap = TemplateMap()


def render_error(request: Request, name: str, context={}, _tmpl=get_jinja2()):
    return _tmpl.TemplateResponse(request, name, context=context)


async def not_found_handler(request: Request, exc: HTTPException):
    return render_error(request, name=tmplmap.err404)


async def unsupported_media_type_handler(
    request: Request,
    exc: UnsupportedMediaTypeException,
):
    return render_error(
        request,
        name=tmplmap.err415,
        context={"bad_mime": exc.mime or "unknown"},
    )


async def bad_request_handler(request: Request, exc: BadRequestExpection):
    # TODO: create specific template for handling bad request error
    return render_error(request, name=tmplmap.err404)
