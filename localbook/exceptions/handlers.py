# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates

from localbook.dependencies import get_jinja2
from localbook.exceptions.exceptions import (
    BadRequestExpection,
    NotFoundException,
    UnsupportedMediaTypeException,
)
from localbook.templates import TemplateMap


def register_handler(exc: type[HTTPException]):
    def d(func):
        func._exception_type = exc
        func._registered = True
        return func

    return d


class ExceptionRender:
    def __init__(
        self,
        app: FastAPI,
        jinja2: Optional[Jinja2Templates] = None,
        tmplmap: Optional[TemplateMap] = None,
    ) -> None:
        self.jinja2 = jinja2 or get_jinja2()
        self.tmplmap = tmplmap or TemplateMap()
        self.app = app

    def configure(self):
        for e, h in self._get_handlers():
            self.app.add_exception_handler(e, h)

    def _get_handlers(self):
        handlers: list[tuple[type[HTTPException], Callable]] = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and getattr(attr, "_registered", False):
                exc_type = getattr(attr, "_exception_type", None)
                if exc_type:
                    handlers.append((exc_type, attr))
        return handlers

    def _base_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ):
        ctx = {}
        # header values
        ctx.update({"view_type": "tree"})
        ctx.update({"toggle_view_url": request.url_for("serve_tree_view", path="")})

        if isinstance(exc, HTTPException):  # type guard check
            if exc.detail:
                ctx.update({"detail": exc.detail})
            if exc.status_code:
                ctx.update({"status_code": exc.status_code})
        return self.jinja2.TemplateResponse(
            request,
            name=self.tmplmap.base_error,
            context=ctx,
        )

    @register_handler(NotFoundException)
    async def not_found(
        self,
        request: Request,
        exc: NotFoundException,
    ):
        return self._base_exception_handler(request, exc)

    @register_handler(UnsupportedMediaTypeException)
    async def unsupported_media_type(
        self,
        request: Request,
        exc: UnsupportedMediaTypeException,
    ):
        return self._base_exception_handler(request, exc)

    @register_handler(BadRequestExpection)
    async def bad_request(
        self,
        request: Request,
        exc: BadRequestExpection,
    ):
        return self._base_exception_handler(request, exc)
