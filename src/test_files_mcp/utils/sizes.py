"""Size parsing and validation utilities."""

from __future__ import annotations

from test_files_mcp.config import get_max_file_size_bytes
from test_files_mcp.models import ToolError, error_result


def resolve_size_bytes(
    size_bytes: int | None = None,
    size_kb: float | None = None,
    size_mb: float | None = None,
) -> int | ToolError:
    """Resolve exactly one size representation to bytes."""
    provided = [
        v
        for v, name in [
            (size_bytes, "size_bytes"),
            (size_kb, "size_kb"),
            (size_mb, "size_mb"),
        ]
        if v is not None
    ]

    if len(provided) == 0:
        return 0

    if len(provided) > 1:
        return error_result(
            "Provide only one of size_bytes, size_kb, or size_mb.",
        )

    if size_bytes is not None:
        resolved = size_bytes
    elif size_kb is not None:
        resolved = int(size_kb * 1024)
    else:
        assert size_mb is not None
        resolved = int(size_mb * 1024 * 1024)

    if resolved < 0:
        return error_result("Size must be non-negative.", requested=resolved)

    max_bytes = get_max_file_size_bytes()
    if resolved > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        requested_mb = resolved / (1024 * 1024)
        return error_result(
            f"Requested file size is {requested_mb:.2f} MB, but the configured "
            f"maximum is {max_mb:.0f} MB. "
            f"Set TEST_FILES_MAX_FILE_SIZE_MB to increase the limit.",
            requested_bytes=resolved,
            maximum_bytes=max_bytes,
        )

    return resolved


def format_bytes(size: int) -> dict[str, float | int]:
    return {
        "size_bytes": size,
        "size_kb": round(size / 1024, 2),
        "size_mb": round(size / (1024 * 1024), 4),
    }
