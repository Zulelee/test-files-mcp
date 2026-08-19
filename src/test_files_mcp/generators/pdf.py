"""PDF file generator."""

from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas

from test_files_mcp.config import get_max_pdf_pages
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path
from test_files_mcp.utils.sizes import resolve_size_bytes

PAGE_SIZES = {
    "a4": A4,
    "letter": letter,
}


def _build_pdf_bytes(
    pages: int,
    page_size: tuple[float, float],
    blank: bool,
    text_per_page: str | None,
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page_size)

    for page_num in range(1, pages + 1):
        if not blank:
            lines = [
                "Test Files MCP",
                f"Page {page_num} of {pages}",
                text_per_page or "Generated test fixture.",
            ]
            y = page_size[1] - 72
            for line in lines:
                c.drawString(72, y, line)
                y -= 20
        if page_num < pages:
            c.showPage()

    c.save()
    return buf.getvalue()


def create_pdf(
    filename: str | None = None,
    pages: int = 1,
    text_per_page: str | None = None,
    page_size: str = "a4",
    target_size_mb: float | None = None,
    blank: bool = False,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a PDF test fixture."""
    max_pages = get_max_pdf_pages()
    if pages < 0:
        return error_result("Page count must be non-negative.", requested=pages)
    if pages > max_pages:
        return error_result(
            f"Requested {pages} pages exceeds configured maximum of {max_pages}. "
            f"Set TEST_FILES_MAX_PDF_PAGES to increase the limit.",
            requested=pages,
            maximum=max_pages,
        )

    ps = page_size.lower()
    if ps not in PAGE_SIZES:
        return error_result(f"Unsupported page size: {page_size}", supported=list(PAGE_SIZES))

    path_result = resolve_output_path(
        filename, output_directory, default_extension="pdf", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    pdf_data = _build_pdf_bytes(pages, PAGE_SIZES[ps], blank, text_per_page)
    padded = False

    if target_size_mb is not None:
        resolved = resolve_size_bytes(None, None, target_size_mb)
        if isinstance(resolved, ToolError):
            return resolved
        target_bytes = resolved
        if len(pdf_data) < target_bytes:
            # Append padding as a comment stream (after %%EOF many readers ignore trailing data)
            padding = b"\n% " + b"X" * (target_bytes - len(pdf_data) - 3)
            if len(pdf_data) + len(padding) < target_bytes:
                padding += b" " * (target_bytes - len(pdf_data) - len(padding))
            pdf_data = pdf_data + padding
            padded = True

    path: Path = path_result
    try:
        path.write_bytes(pdf_data)
    except OSError as exc:
        return error_result(f"Failed to write PDF: {exc}")

    actual_size = path.stat().st_size
    target_bytes_result: int | None = None
    if target_size_mb is not None:
        resolved_target = resolve_size_bytes(None, None, target_size_mb)
        if isinstance(resolved_target, ToolError):
            return resolved_target
        target_bytes_result = resolved_target

    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="application/pdf",
        size_bytes=actual_size,
        pages=pages,
        page_size=ps,
        blank=blank,
        padded=padded,
        target_size_bytes=target_bytes_result,
    )
