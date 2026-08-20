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

import pymupdf

from . import config

DEFAULT_DPI = 300  # dot-matrix + handwriting need high DPI to stay legible


def _zoom_matrix(dpi: int) -> "pymupdf.Matrix":
    """72 pt/in is the PDF unit; scale so the raster lands at *dpi*."""
    z = dpi / 72.0
    return pymupdf.Matrix(z, z)


def _page_name(page_index: int, total: int) -> str:
    width = max(2, len(str(total)))
    return f"page_{page_index + 1:0{width}d}.png"


def render_pages(
    pdf_path: Path = config.SOURCE_PDF,
    out_dir: Path = config.PAGE_IMAGE_DIR,
    dpi: int = DEFAULT_DPI,
) -> list[Path]:
    """Render all pages of *pdf_path* to PNGs under *out_dir*; return paths."""
    pdf_path, out_dir = Path(pdf_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    mat = _zoom_matrix(dpi)
    paths: list[Path] = []
    with pymupdf.open(pdf_path) as doc:
        total = doc.page_count
        for i in range(total):
            pix = doc[i].get_pixmap(matrix=mat)
            fn = out_dir / _page_name(i, total)
            pix.save(fn)
            paths.append(fn)
    return paths


def render_page(
    pdf_path: Path = config.SOURCE_PDF,
    page_index: int = 0,
    dpi: int = DEFAULT_DPI,
    out_dir: Path = config.PAGE_IMAGE_DIR,
) -> Path:
    """Render a single 0-based page to a PNG and return its path."""
    pdf_path, out_dir = Path(pdf_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    mat = _zoom_matrix(dpi)
    with pymupdf.open(pdf_path) as doc:
        total = doc.page_count
        pix = doc[page_index].get_pixmap(matrix=mat)
        fn = out_dir / _page_name(page_index, total)
        pix.save(fn)
    return fn


if __name__ == "__main__":
    out = render_pages()
    print(f"Rendered {len(out)} pages -> {out[0].parent}")
    for p in out:
        print("  ", p.name)
