# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 18.03.2025 17:21
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================


class _LBTmplPagesMap:
    def __init__(self) -> None:
        self.err404 = "pages/404.jinja"
        self.err415 = "pages/415.jinja"
        self.serve_list_view = "pages/list_view.jinja"
        self.serve_tree_view = "pages/tree_view.jinja"
        self.pdfviewer = "pages/pdfviewer_native.jinja"


class LBTmplMap:
    def __init__(self) -> None:
        self.pages = _LBTmplPagesMap()
