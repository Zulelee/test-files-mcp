"""MCP server for Test Files MCP."""

from __future__ import annotations

import logging

from mcp.server import MCPServer

from test_files_mcp import __version__
from test_files_mcp.corruption.corrupt import create_corrupted_file, create_edge_case_filename
from test_files_mcp.generators.archive import create_archive
from test_files_mcp.generators.audio import create_audio
from test_files_mcp.generators.binary import create_dummy_file
from test_files_mcp.generators.csv import create_csv
from test_files_mcp.generators.images import create_image
from test_files_mcp.generators.json import create_json
from test_files_mcp.generators.pdf import create_pdf
from test_files_mcp.models import ToolError, ToolSuccess
from test_files_mcp.utils.files import inspect_file

logging.basicConfig(level=logging.INFO)

mcp = MCPServer(
    "Test Files MCP",
    instructions=(
        "Generate test files for development, QA, upload testing, parser testing, "
        "validation testing, and edge-case testing. Creates files locally and returns "
        "absolute paths with metadata."
    ),
    version=__version__,
)


@mcp.tool()
def create_dummy_file_tool(
    filename: str | None = None,
    size_bytes: int | None = None,
    size_kb: float | None = None,
    size_mb: float | None = None,
    content: str = "random",
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Create a dummy file of a requested size for testing file uploads,
    storage limits, validators, APIs, and other file-handling code.

    Examples: 1 byte file, 500 KB, 20 MB, 1 GB (within configured limits).
    Content can be random bytes, zeros, or repeating text.
  """
    return create_dummy_file(
        filename=filename,
        size_bytes=size_bytes,
        size_kb=size_kb,
        size_mb=size_mb,
        content=content,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_image_tool(
    filename: str | None = None,
    format: str = "png",
    width: int = 1024,
    height: int = 1024,
    target_size_kb: float | None = None,
    target_size_mb: float | None = None,
    background: str = "808080",
    pattern: str = "noise",
    quality: int = 85,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a test image (JPEG, PNG, WEBP, BMP) with configurable dimensions,
    patterns, and approximate target file size.

    Examples: 8000x8000 JPEG, approximately 20 MB JPEG, checkerboard PNG.
    """
    return create_image(
        filename=filename,
        format=format,
        width=width,
        height=height,
        target_size_kb=target_size_kb,
        target_size_mb=target_size_mb,
        background=background,
        pattern=pattern,
        quality=quality,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_pdf_tool(
    filename: str | None = None,
    pages: int = 1,
    text_per_page: str | None = None,
    page_size: str = "a4",
    target_size_mb: float | None = None,
    blank: bool = False,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a PDF test fixture with a specified number of pages.

    Examples: 100 blank pages, 200-page PDF with sample text, ~30 MB PDF.
    """
    return create_pdf(
        filename=filename,
        pages=pages,
        text_per_page=text_per_page,
        page_size=page_size,
        target_size_mb=target_size_mb,
        blank=blank,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_csv_tool(
    filename: str | None = None,
    rows: int = 10,
    columns: int = 5,
    headers: list[str] | None = None,
    delimiter: str = ",",
    include_header: bool = True,
    encoding: str = "utf-8",
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a CSV test fixture with synthetic data, streamed to disk.

    Examples: 0 rows, 100,000 rows, 1,000,000 rows (within configured limits).
    """
    return create_csv(
        filename=filename,
        rows=rows,
        columns=columns,
        headers=headers,
        delimiter=delimiter,
        include_header=include_header,
        encoding=encoding,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_json_tool(
    filename: str | None = None,
    items: int = 5,
    depth: int = 1,
    pretty: bool = True,
    malformed: bool = False,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a JSON test fixture. Set malformed=true for intentionally invalid JSON.

    Examples: valid JSON array, malformed JSON with trailing comma or missing bracket.
    """
    return create_json(
        filename=filename,
        items=items,
        depth=depth,
        pretty=pretty,
        malformed=malformed,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_archive_tool(
    filename: str | None = None,
    files: int = 5,
    file_size_kb: float = 1.0,
    empty: bool = False,
    nested: bool = False,
    compression: str = "deflated",
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a ZIP archive test fixture.

    Examples: empty ZIP, ZIP with 100 files, nested directory structure.
    """
    return create_archive(
        filename=filename,
        files=files,
        file_size_kb=file_size_kb,
        empty=empty,
        nested=nested,
        compression=compression,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_audio_tool(
    filename: str | None = None,
    duration_seconds: float = 5.0,
    sample_rate: int = 44100,
    channels: int = 1,
    tone_hz: float = 440.0,
    silence: bool = False,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a WAV audio test fixture.

    Examples: 30-second silent WAV, 5-second 440 Hz tone.
    """
    return create_audio(
        filename=filename,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        channels=channels,
        tone_hz=tone_hz,
        silence=silence,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_corrupted_file_tool(
    source_path: str | None = None,
    file_type: str = "generic",
    corruption: str = "random_bytes",
    severity: float = 0.5,
    filename: str | None = None,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Create a corrupted copy of a file for testing error handling. Never modifies the original.

    Examples: corrupted JPEG, PDF truncated at 70%, ZIP with random bytes, PNG with wrong extension.
    """
    return create_corrupted_file(
        source_path=source_path,
        file_type=file_type,
        corruption=corruption,
        severity=severity,
        filename=filename,
        seed=seed,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def create_edge_case_filename_tool(
    case: str = "unicode",
    extension: str = "txt",
    size_bytes: int = 64,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a file with an edge-case filename for upload/path testing.

    Cases: spaces, unicode, very_long, multiple_dots, uppercase_extension, no_extension, hidden.
    """
    return create_edge_case_filename(
        case=case,
        extension=extension,
        size_bytes=size_bytes,
        output_directory=output_directory,
        overwrite=overwrite,
    )


@mcp.tool()
def inspect_file_tool(path: str) -> ToolSuccess | ToolError:
    """Inspect a generated test file and return metadata (size, MIME type, SHA256, etc.)."""
    return inspect_file(path)


def main() -> None:
    """Entry point for the Test Files MCP stdio server."""
    mcp.run()


if __name__ == "__main__":
    main()
