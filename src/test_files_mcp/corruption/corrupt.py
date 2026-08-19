"""File corruption utilities for testing parsers and validators."""

from __future__ import annotations

import random
from pathlib import Path

from test_files_mcp.config import get_output_dir
from test_files_mcp.generators.archive import create_archive
from test_files_mcp.generators.binary import create_dummy_file
from test_files_mcp.generators.csv import create_csv
from test_files_mcp.generators.images import create_image
from test_files_mcp.generators.json import create_json
from test_files_mcp.generators.pdf import create_pdf
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import (
    ensure_output_directory,
    resolve_output_path,
    validate_existing_path,
)

CORRUPTION_TYPES = [
    "truncate",
    "random_bytes",
    "bad_header",
    "bad_extension",
    "empty",
    "append_garbage",
]

FILE_TYPE_EXTENSIONS = {
    "jpeg": ".jpg",
    "png": ".png",
    "pdf": ".pdf",
    "json": ".json",
    "csv": ".csv",
    "zip": ".zip",
    "generic": ".bin",
}


def _generate_source(
    file_type: str,
    seed: int | None,
    output_directory: str | None,
) -> ToolSuccess | ToolError:
    """Generate a fresh fixture to corrupt when no source_path is given."""
    ft = file_type.lower()
    if ft in {"jpeg", "jpg", "png", "webp", "bmp"}:
        fmt = "jpeg" if ft in {"jpeg", "jpg"} else ft
        return create_image(
            format=fmt,
            seed=seed,
            output_directory=output_directory,
            overwrite=True,
        )
    if ft == "pdf":
        return create_pdf(pages=3, output_directory=output_directory, overwrite=True)
    if ft == "json":
        return create_json(items=5, output_directory=output_directory, overwrite=True)
    if ft == "csv":
        return create_csv(rows=10, output_directory=output_directory, overwrite=True)
    if ft == "zip":
        return create_archive(files=3, output_directory=output_directory, overwrite=True)
    return create_dummy_file(
        size_kb=10, content="random", seed=seed, output_directory=output_directory, overwrite=True
    )


def _apply_corruption(
    data: bytes,
    corruption: str,
    severity: float,
    rng: random.Random,
) -> tuple[bytes, dict]:
    """Apply corruption to raw bytes and return corrupted data with details."""
    severity = max(0.0, min(1.0, severity))
    details: dict = {
        "corruption": corruption,
        "severity": severity,
        "original_size_bytes": len(data),
    }

    if corruption == "empty":
        details["description"] = "Replaced entire file with empty content."
        return b"", details

    if corruption == "truncate":
        keep_ratio = max(0.01, 1.0 - severity)
        new_len = max(1, int(len(data) * keep_ratio))
        details["description"] = f"Truncated file to {keep_ratio:.0%} of original size."
        details["truncated_to_bytes"] = new_len
        return data[:new_len], details

    if corruption == "random_bytes":
        data = bytearray(data)
        num_changes = max(1, int(len(data) * severity * 0.1))
        positions = [rng.randint(0, max(len(data) - 1, 0)) for _ in range(num_changes)]
        for pos in positions:
            data[pos] = rng.randint(0, 255)
        details["description"] = f"Inserted random bytes at {num_changes} positions."
        details["positions_changed"] = num_changes
        return bytes(data), details

    if corruption == "bad_header":
        data = bytearray(data)
        header_len = min(16, len(data))
        for i in range(header_len):
            data[i] = rng.randint(0, 255)
        details["description"] = f"Corrupted first {header_len} bytes (header)."
        return bytes(data), details

    if corruption == "append_garbage":
        garbage_size = max(1, int(len(data) * severity))
        garbage = rng.randbytes(garbage_size)
        details["description"] = f"Appended {garbage_size} bytes of garbage."
        details["garbage_bytes"] = garbage_size
        return data + garbage, details

    if corruption == "bad_extension":
        details["description"] = "File content unchanged; extension will be swapped."
        details["note"] = "Extension change applied at output path."
        return data, details

    raise ValueError(f"Unknown corruption type: {corruption}")


def create_corrupted_file(
    source_path: str | None = None,
    file_type: str = "generic",
    corruption: str = "random_bytes",
    severity: float = 0.5,
    filename: str | None = None,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Create a corrupted copy of a file for testing error handling."""
    if corruption not in CORRUPTION_TYPES:
        return error_result(
            f"Unsupported corruption type: {corruption}",
            supported=CORRUPTION_TYPES,
        )

    rng = random.Random(seed)
    original_path: Path | None = None

    if source_path:
        allowed = [ensure_output_directory(output_directory), get_output_dir().resolve()]
        validated = validate_existing_path(source_path, allowed_directories=allowed)
        if isinstance(validated, ToolError):
            return validated
        original_path = validated
        source_data = original_path.read_bytes()
    else:
        generated = _generate_source(file_type, seed, output_directory)
        if isinstance(generated, ToolError):
            return generated
        original_path = Path(generated.path)
        source_data = original_path.read_bytes()

    try:
        corrupted_data, corruption_details = _apply_corruption(
            source_data, corruption, severity, rng
        )
    except ValueError as exc:
        return error_result(str(exc))

    # Determine output filename
    if filename is None:
        stem = f"corrupted-{original_path.stem}"
        if corruption == "bad_extension":
            ext = FILE_TYPE_EXTENSIONS.get(file_type.lower(), ".txt")
            # Swap to a wrong extension
            wrong_ext = ".txt" if ext != ".txt" else ".bin"
            filename = f"{stem}{wrong_ext}"
        else:
            filename = f"{stem}{original_path.suffix or '.bin'}"

    path_result = resolve_output_path(
        filename, output_directory, overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    output_path: Path = path_result
    try:
        output_path.write_bytes(corrupted_data)
    except OSError as exc:
        return error_result(f"Failed to write corrupted file: {exc}")

    corruption_details["source_path"] = str(original_path.resolve())
    corruption_details["source_unchanged"] = True

    # Verify original unchanged
    if original_path.exists():
        corruption_details["source_size_bytes"] = original_path.stat().st_size

    mime = "application/octet-stream"
    return success_result(
        path=str(output_path.resolve()),
        filename=output_path.name,
        file_type=mime,
        size_bytes=output_path.stat().st_size,
        **corruption_details,
    )


def create_edge_case_filename(
    case: str = "unicode",
    extension: str = "txt",
    size_bytes: int = 64,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a file with an edge-case filename for upload/path testing."""
    cases: dict[str, str] = {
        "spaces": f"file with spaces.{extension}",
        "unicode": f"résumé-测试.{extension}",
        "very_long": f"{'a' * 200}.{extension}",
        "multiple_dots": f"invoice.final.final.REALLYFINAL.{extension}",
        "uppercase_extension": f"IMAGE.{extension.upper()}",
        "no_extension": "README",
        "hidden": f".hidden-file.{extension}",
    }

    if case not in cases:
        return error_result(
            f"Unsupported edge case: {case}",
            supported=list(cases.keys()),
        )

    filename = cases[case]

    # Safety check for OS compatibility
    try:
        ensure_output_directory(output_directory)
        # On Windows, certain names are reserved
        reserved = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {
            f"LPT{i}" for i in range(1, 10)
        }
        stem = Path(filename).stem.upper().split(".")[0]
        if stem in reserved:
            return error_result(
                f"Filename case '{case}' resolves to a reserved name on Windows.",
                filename=filename,
                suggestion="Use a different case type.",
            )
    except (OSError, ValueError) as exc:
        return error_result(
            f"Cannot safely create filename for case '{case}' on this OS.",
            reason=str(exc),
        )

    path_result = resolve_output_path(
        filename, output_directory, overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    path: Path = path_result
    content = f"Edge case filename test: {case}\n".encode() + b"X" * max(size_bytes - 32, 0)
    try:
        path.write_bytes(content[:size_bytes] if size_bytes > 0 else b"")
    except OSError as exc:
        return error_result(f"Failed to write file: {exc}")

    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="text/plain",
        size_bytes=path.stat().st_size,
        case=case,
        extension=extension,
    )
