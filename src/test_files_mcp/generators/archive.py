"""ZIP archive generator."""

from __future__ import annotations

import random
import zipfile
from pathlib import Path

from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path


def create_archive(
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
    """Generate a ZIP test fixture."""
    if files < 0:
        return error_result("File count must be non-negative.", requested=files)

    comp = zipfile.ZIP_DEFLATED if compression == "deflated" else zipfile.ZIP_STORED
    if compression not in {"stored", "deflated"}:
        return error_result(
            f"Unsupported compression: {compression}",
            supported=["stored", "deflated"],
        )

    path_result = resolve_output_path(
        filename, output_directory, default_extension="zip", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    rng = random.Random(seed)
    path: Path = path_result
    file_size = int(file_size_kb * 1024)

    try:
        with zipfile.ZipFile(path, "w", compression=comp) as zf:
            if empty:
                pass
            else:
                for i in range(1, files + 1):
                    if nested:
                        arcname = f"dir_{i // 10 + 1}/subdir/file_{i:04d}.txt"
                    else:
                        arcname = f"file_{i:04d}.txt"
                    content = rng.randbytes(file_size) if file_size > 0 else b""
                    zf.writestr(arcname, content)
    except OSError as exc:
        return error_result(f"Failed to write ZIP: {exc}")

    actual_size = path.stat().st_size

    # Count contained files
    with zipfile.ZipFile(path, "r") as zf:
        contained = len(zf.namelist())

    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="application/zip",
        size_bytes=actual_size,
        files=contained,
        empty=empty,
        nested=nested,
        compression=compression,
        seed=seed,
    )
