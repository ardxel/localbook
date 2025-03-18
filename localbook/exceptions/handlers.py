# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 17:21
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================





from fastapi import HTTPException, Request

from localbook.dependencies import Deps

from .exceptions import UnsupportedMediaTypeException

tmpl = Deps().get_tmpl()


async def not_found_handler(request: Request, exc: HTTPException):
    return tmpl.TemplateResponse(
        request,
        name="pages/404.html.jinja",
    )


async def unsupported_media_type_handler(
    request: Request,
    exc: UnsupportedMediaTypeException,
):
    return tmpl.TemplateResponse(
        request,
        name="pages/415.html.jinja",
        context={"bad_mime": exc.mime or "unknown"},
    )
