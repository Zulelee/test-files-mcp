"""Tests for PDF generation."""

from __future__ import annotations

from pathlib import Path

from test_files_mcp.generators.pdf import create_pdf

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore[misc, assignment]


def test_page_count(output_dir: Path) -> None:
    result = create_pdf(
        filename="pages.pdf",
        pages=10,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["pages"] == 10
    assert Path(result.path).exists()
    assert result.size_bytes > 0


def test_blank_pages(output_dir: Path) -> None:
    result = create_pdf(
        filename="blank.pdf",
        pages=5,
        blank=True,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["blank"] is True


def test_readable_pdf(output_dir: Path) -> None:
    if PdfReader is None:
        return  # pypdf not installed; basic existence check suffices
    result = create_pdf(
        filename="readable.pdf",
        pages=3,
        output_directory=str(output_dir),
        overwrite=True,
    )
    reader = PdfReader(result.path)
    assert len(reader.pages) == 3
