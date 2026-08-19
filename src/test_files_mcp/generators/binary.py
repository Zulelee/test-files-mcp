"""Binary/dummy file generator."""

from __future__ import annotations

import random
from pathlib import Path

from test_files_mcp.config import CHUNK_SIZE_BYTES
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.files import guess_mime_type
from test_files_mcp.utils.paths import resolve_output_path
from test_files_mcp.utils.sizes import resolve_size_bytes

TEXT_SAMPLE = (
    "Test Files MCP dummy content line.\n"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\n"
)


def create_dummy_file(
    filename: str | None = None,
    size_bytes: int | None = None,
    size_kb: float | None = None,
    size_mb: float | None = None,
    content: str = "random",
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a generic file with an exact byte size."""
    resolved_size = resolve_size_bytes(size_bytes, size_kb, size_mb)
    if isinstance(resolved_size, ToolError):
        return resolved_size

    path_result = resolve_output_path(
        filename, output_directory, default_extension="bin", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    rng = random.Random(seed)
    path: Path = path_result

    try:
        with path.open("wb") as fh:
            remaining = resolved_size
            if content == "zeros":
                zero_chunk = b"\x00" * min(CHUNK_SIZE_BYTES, max(remaining, 1))
                while remaining > 0:
                    chunk_size = min(len(zero_chunk), remaining)
                    fh.write(zero_chunk[:chunk_size])
                    remaining -= chunk_size
            elif content == "text":
                text_bytes = TEXT_SAMPLE.encode("utf-8")
                while remaining > 0:
                    chunk_size = min(len(text_bytes), remaining)
                    fh.write(text_bytes[:chunk_size])
                    remaining -= chunk_size
            else:  # random
                while remaining > 0:
                    chunk_size = min(CHUNK_SIZE_BYTES, remaining)
                    fh.write(rng.randbytes(chunk_size))
                    remaining -= chunk_size
    except OSError as exc:
        return error_result(f"Failed to write file: {exc}")

    actual_size = path.stat().st_size
    mime = guess_mime_type(path)

    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type=mime,
        size_bytes=actual_size,
        content_type=content,
        seed=seed,
    )
