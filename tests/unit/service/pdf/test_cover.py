# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:23
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

from typing import Any
from unittest.mock import MagicMock, Mock, mock_open

from pytest import MonkeyPatch, fixture
from utils import FSTree, mock_cover_info
from utils import mock_pdf_file as pdf_file

from localbook.lib.filesystem.pdf import PDFFile
from localbook.service.book.cover import (
    BookCoverGenerator,
    BookCoverMetadata,
    BookCoverService,
    _BookCoverInfo,
)


class TestBookCoverService:
    def mock_metadata(self, covers: list[_BookCoverInfo]):
        m = MagicMock()
        m.read.return_value = MagicMock(
            covers=covers,
            timestamp=1.1,
            count=len(covers),
        )
        return m

    def test_get_cover(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("os.path.relpath", lambda path, base: path)
        monkeypatch.setattr("os.makedirs", lambda path: None)

        cover_info = mock_cover_info(
            "/root/test.pdf",
            pdf_nid="nid1",
            thumbnails={"desktop": "desktop.jpeg", "mobile": "mobile.jpeg"},
        )

        mock_metadata = self.mock_metadata([cover_info])
        service = BookCoverService(m=mock_metadata)
        mock_metadata.read.assert_called_once()

        file = pdf_file(cover_info.original, None, _nid=str(cover_info.pdf_nid))

        assert service.get_cover(file, "desktop") == "desktop.jpeg"
        assert service.get_cover(file, "mobile") == "mobile.jpeg"


class TestBookCoverGenerator:
    @fixture
    def mock_pdf_file(self) -> PDFFile:
        return pdf_file("/root/file.pdf", None, _nid="pdf-nid")

    @fixture
    def image_settings(self) -> list[Any]:
        return [
            {
                "device": "desktop-test",
                "dpi": 150,
                "quality": 85,
                "page_x": 170,
                "page_y": 240,
                "format": "JPEG",
            },
            {
                "device": "mobile-test",
                "dpi": 150,
                "quality": 85,
                "page_x": 150,
                "page_y": 212,
                "format": "JPEG",
            },
        ]

    @fixture
    def mock_cover_info(self, mock_pdf_file) -> _BookCoverInfo:
        return mock_cover_info(
            mock_pdf_file._path,
            pdf_nid=mock_pdf_file.nid,
            thumbnails={
                "desktop-test": "desktop-test.jpeg",
                "mobile-test": "mobile-test.jpeg",
            },
        )

    @fixture
    def mock_fstree(self, mock_pdf_file) -> FSTree:
        m = MagicMock()
        m.pdf_list.return_value = iter([mock_pdf_file])
        return m

    @fixture
    def stub_converter(self) -> tuple[Mock, Mock, Mock]:
        image2 = Mock()
        image2.save = Mock()

        image1 = Mock()
        image1.resize.return_value = image2

        converter = Mock(return_value=[image1])
        return converter, image1, image2

    @fixture
    def mock_rmtree(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("shutil.rmtree", lambda x: None)

    @fixture
    def mock_makedirs(self, monkeypatch: MonkeyPatch):
        monkeypatch.setattr("os.makedirs", lambda path, exist_ok: None)

    def test_generate(
        self,
        mock_fstree: FSTree,
        stub_converter: MagicMock,
        image_settings: list[Any],
        mock_rmtree: None,
        mock_makedirs: None,
    ):
        mock_metadata = MagicMock()
        mock_metadata.save = MagicMock()
        mock_metadata.read = MagicMock()

        mock_fstree = mock_fstree
        converter, resizer, saver = stub_converter

        generator = BookCoverGenerator(
            "/test",
            image_settings=image_settings,
            metadata=mock_metadata,
            fstree=mock_fstree,
            converter=converter,
        )

        generator.generate(cache=False)
        mock_metadata.save.assert_called_once()

        assert converter.call_count == 2
        assert resizer.resize.call_count == 1
        assert saver.save.call_count == 1


class TestBookCoverMetadata:
    @fixture
    def sample_info(self):
        return _BookCoverInfo(
            original="/root/test.pdf",
            pdf_nid="pdf-nid",
            thumbnails={"desktop": "desktop.jpeg"},
            mtime=123456789.0,
        )

    def test_metadata_save(
        self,
        sample_info: _BookCoverInfo,
        monkeypatch: MonkeyPatch,
    ):
        mopen = mock_open()
        monkeypatch.setattr("builtins.open", mopen)
        mjson_dump = MagicMock()
        monkeypatch.setattr("json.dump", mjson_dump)
        monkeypatch.setattr("os.path.exists", lambda _: True)
        monkeypatch.setattr("os.makedirs", lambda path, exist_ok: None)

        digest_instance = MagicMock()
        digest = MagicMock(return_value=digest_instance)
        monkeypatch.setattr(
            "localbook.service.book.cover._BookCoverMetadataDigest", digest
        )

        metadata = BookCoverMetadata("/dump")
        metadata.save([sample_info])
        assert mopen.call_args[0][0] == "/dump"
        assert mopen.call_args[0][1] == "w"
        assert digest_instance.to_dict.call_count == 1
