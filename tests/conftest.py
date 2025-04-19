# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 11.04.2025 00:23
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import os

from pytest import MonkeyPatch, fixture

import localbook.lib.filesystem.file


@fixture
def mock_read_mime(monkeypatch: MonkeyPatch):
    def f(path, *args, **kwargs):
        if path.endswith(".pdf"):
            return "application/pdf"
        else:
            return "text/plain"

    monkeypatch.setattr(localbook.lib.filesystem.file, "_read_mime", f)


@fixture
def mock_os_stat(monkeypatch: MonkeyPatch):
    class MockStatResult:
        @property
        def st_size(self):
            return 1

    def f(*args, **kwargs):
        return MockStatResult()

    monkeypatch.setattr(os, "stat", f)


@fixture
def mock_os_getmtime(monkeypatch: MonkeyPatch):
    def f(*args, **kwargs):
        return 3.14

    monkeypatch.setattr(os.path, "getmtime", f)
