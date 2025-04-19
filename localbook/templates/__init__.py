# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


class TemplateMap:
    def __init__(self) -> None:
        self.err404 = "pages/404.jinja"
        self.err415 = "pages/415.jinja"
        self.serve_list_view = "pages/list_view.jinja"
        self.serve_tree_view = "pages/tree_view.jinja"
        self.pdfviewer = "pages/pdfviewer_native.jinja"
