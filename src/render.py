"""render.py — rasterise the text-less scanned BoQ into page images.

The source PDF has NO text layer (each page is one scanned image), so before
anything can be extracted the pages must be rendered to bitmaps. PyMuPDF is
used because it needs no external binary (poppler/ImageMagick) on Windows.

Public API
----------
render_pages(pdf_path, out_dir, dpi) -> list[Path]
    Render every page to a PNG and return the image paths (page order).
render_page(pdf_path, page_index, dpi) -> Path
    Render a single page (handy for the vision extractor / previews).
"""
from __future__ import annotations

from pathlib import Path

from . import config

DEFAULT_DPI = 300  # dot-matrix + handwriting need high DPI to stay legible


def render_pages(
    pdf_path: Path = config.SOURCE_PDF,
    out_dir: Path = config.PAGE_IMAGE_DIR,
    dpi: int = DEFAULT_DPI,
) -> list[Path]:
    """Render all pages of *pdf_path* to PNGs under *out_dir*; return paths."""
    raise NotImplementedError  # TODO: implement in the render step


def render_page(
    pdf_path: Path = config.SOURCE_PDF,
    page_index: int = 0,
    dpi: int = DEFAULT_DPI,
    out_dir: Path = config.PAGE_IMAGE_DIR,
) -> Path:
    """Render a single 0-based page to a PNG and return its path."""
    raise NotImplementedError  # TODO: implement in the render step
