# ================================================================
# @Project: LocalBook
# @Author: Vasily Bobnev (@ardxel)
# @License: MIT License
# @Date: 19.04.2025 16:27
# @Repository: https://github.com/ardxel/localbook.git
# ================================================================

import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional, Self

from pdf2image import convert_from_path
from PIL.Image import Image, Resampling

from localbook.config import COVER_DIR, COVER_METADATA_FILE
from localbook.dependencies import get_fstree
from localbook.lib.filesystem.node import NID
from localbook.lib.filesystem.pdf import PDFFile
from localbook.lib.filesystem.tree import FSTree

DEFAULT_IMAGE_SETTINGS = [
    {
        "device": "desktop",
        "dpi": 150,
        "quality": 85,
        "page_x": 170,
        "page_y": 240,
        "format": "JPEG",
    },
    {
        "device": "laptop",
        "dpi": 150,
        "quality": 85,
        "page_x": 150,
        "page_y": 212,
        "format": "JPEG",
    },
    {
        "device": "tablet",
        "dpi": 150,
        "quality": 85,
        "page_x": 140,
        "page_y": 198,
        "format": "JPEG",
    },
    {
        "device": "mobile",
        "dpi": 150,
        "quality": 85,
        "page_x": 120,
        "page_y": 170,
        "format": "JPEG",
    },
]


@dataclass
class _ImageSettings:
    device: str
    dpi: int
    quality: int
    page_x: int
    page_y: int
    format: str

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


@dataclass
class _BookCoverInfo:
    original: str
    pdf_nid: NID | str
    thumbnails: dict[str, str]
    mtime: float

    @classmethod
    def from_dict(cls, **kwargs) -> Self:
        return cls(
            pdf_nid=kwargs["nid"],
            original=kwargs["original"],
            thumbnails=kwargs["thumbnails"],
            mtime=kwargs["mtime"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "nid": self.pdf_nid,
            "original": self.original,
            "thumbnails": self.thumbnails,
            "mtime": self.mtime,
        }


class _BookCoverMetadataDigest:
    def __init__(
        self,
        covers: list[_BookCoverInfo],
        timestamp: datetime,
        count: int,
    ) -> None:
        self.covers = covers
        self.timestamp = timestamp
        self.count = count

    @classmethod
    def from_dict(cls, **kwargs) -> Self:
        return cls(
            covers=[_BookCoverInfo.from_dict(**c) for c in kwargs["covers"]],
            timestamp=kwargs["timestamp"],
            count=kwargs["count"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "covers": [c.to_dict() for c in self.covers],
            "timestamp": str(self.timestamp),
            "count": self.count,
        }


class BookCoverMetadata:
    def __init__(
        self,
        metadata_file: Optional[str] = None,
    ) -> None:
        self.data_fp = metadata_file or COVER_METADATA_FILE

    def save(self, data: list[_BookCoverInfo]) -> None:
        m = _BookCoverMetadataDigest(
            covers=data,
            timestamp=datetime.now(timezone.utc),
            count=len(data),
        )

        if not os.path.exists(os.path.dirname(self.data_fp)):
            os.makedirs(os.path.dirname(self.data_fp), exist_ok=True)
        with open(self.data_fp, "w") as f:
            json.dump(m.to_dict(), f, indent=2)

    def read(self) -> _BookCoverMetadataDigest:
        if not os.path.exists(self.data_fp):
            raise ValueError("metadata file is not exists")
        with open(self.data_fp, "r") as f:
            d = json.load(f)
            m = _BookCoverMetadataDigest.from_dict(**d)
            return m

    def clear(self) -> None:
        if os.path.exists(self.data_fp):
            os.remove(self.data_fp)


class BookCoverGenerator:
    """PDF image generator as covers.

    Will generate first page of pdf file as cover image in specific patterned data.
    """

    _generated = False

    def __init__(
        self,
        cover_dir: Optional[str] = None,
        image_settings: Optional[list[Any]] = None,
        metadata: Optional[BookCoverMetadata] = None,
        fstree: Optional[FSTree] = None,
        **kwargs,
    ) -> None:
        self.logger = logging.getLogger("localbook")
        self.cover_dir = cover_dir or COVER_DIR
        image_settings = image_settings or DEFAULT_IMAGE_SETTINGS
        self.image_settings = [_ImageSettings.from_dict(i) for i in image_settings]
        self.fstree = fstree or get_fstree()
        self.metadata = metadata or BookCoverMetadata()
        self.converter: Callable[..., list[Image]] = kwargs.get(
            "converter", convert_from_path
        )

    def _generate_unsafe(self, cache=True) -> None:
        if self._generated:
            return

        try:
            artefact = self.metadata.read()
        except Exception as e:
            artefact = None
        pdf_files = self.fstree.pdf_list()

        if cache and artefact:
            cached = {c.original: c for c in artefact.covers}
            to_gen: list[PDFFile] = []
            valid: list[_BookCoverInfo] = []
            for pf in pdf_files:
                cached_cover = cached.get(pf._path)

                # if file covers are exists and not modified
                if cached_cover and cached_cover.mtime == pf.mtime:
                    valid.append(cached_cover)
                else:
                    to_gen.append(pf)

            old_paths = set(cached.keys())
            new_paths = {pf._path for pf in pdf_files}
            orphaned = old_paths - new_paths
            # remaining covers that haven't been paired with existing pdf files
            for pf in orphaned:
                shutil.rmtree(
                    path=os.path.join(self.cover_dir, cached[pf].pdf_nid),
                    ignore_errors=False,
                )

            extra_covers = [self._generate_cover(pf) for pf in to_gen]
            valid += extra_covers
            self.metadata.save(valid)
        else:
            os.makedirs(self.cover_dir, exist_ok=True)
            covers = [self._generate_cover(pf) for pf in pdf_files]
            self.metadata.save(covers)

        self._generated = True
        self.logger.info("BookCoverGenerator: Book covers generated successfully.")

    def _generate_cover(
        self,
        pf: PDFFile,
    ) -> _BookCoverInfo:
        """Generate cover by the fist page of pdf file."""
        info = _BookCoverInfo(
            original=pf._path,
            pdf_nid=pf.nid,
            thumbnails={},
            mtime=pf.mtime,
        )
        for s in self.image_settings:
            ppm_image = self.converter(
                pdf_path=pf._path,
                dpi=s.dpi,
                first_page=1,
                last_page=1,
            ).pop()

            image = ppm_image.resize(
                (s.page_x, s.page_y),
                resample=Resampling.LANCZOS,
            )

            nid_dir = os.path.join(self.cover_dir, str(pf.nid))
            if not os.path.exists(nid_dir):
                os.makedirs(nid_dir, exist_ok=True)
            # cover file
            cfp = os.path.join(nid_dir, f"{s.device}.{s.format.lower()}")
            image.save(
                fp=cfp,
                format=s.format,
                quality=s.quality,
            )
            info.thumbnails[s.device] = cfp
        return info

    def clear_data(self) -> None:
        if os.path.exists(self.cover_dir):
            shutil.rmtree(self.cover_dir)
        os.makedirs(self.cover_dir, exist_ok=True)
        m = BookCoverMetadata()
        m.clear()

    def generate(self, cache=True) -> None:
        """will creates covers for every device inside unique `nid` dir"""
        try:
            self._generate_unsafe(cache=cache)
        except Exception as e:
            self.logger.warning(f"BookCoverGenerator Error: {e}")
            self.clear_data()
            self._generate_unsafe(cache=False)


class BookCoverService:
    def __init__(
        self,
        m: Optional[BookCoverMetadata] = None,
    ) -> None:
        m = m or BookCoverMetadata()
        self.metadata = m.read()

    def get_cover(self, pdf_file: PDFFile, device: str = "desktop") -> str:
        default_cover = ""
        if self.metadata is None:
            return default_cover
        pdf_cover_data: None | _BookCoverInfo = None
        for cover in self.metadata.covers:
            if cover.pdf_nid == str(pdf_file.nid):
                pdf_cover_data = cover
        if pdf_cover_data is None:
            return default_cover

        cover_file = pdf_cover_data.thumbnails[device]
        return cover_file
