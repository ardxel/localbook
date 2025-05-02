# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateMap:
    base_error: str = "pages/base_error.jinja"
    serve_list_view: str = "pages/list_view.jinja"
    serve_tree_view: str = "pages/tree_view.jinja"
    book_viewer_mozilla: str = "pages/book_viewer_mozilla.jinja"
