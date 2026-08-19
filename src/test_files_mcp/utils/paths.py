"""Filesystem path security and resolution utilities."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from test_files_mcp.config import get_output_dir
from test_files_mcp.models import ToolError, error_result

UNSAFE_FILENAME_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
TRAVERSAL_PATTERN = re.compile(r"(^|[/\\])\.\.([/\\]|$)")


class PathSecurityError(Exception):
    """Raised when a path operation violates security rules."""


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a filename (not full path)."""
    name = filename.strip().replace("\x00", "")
    if TRAVERSAL_PATTERN.search(name):
        raise PathSecurityError("Filename must not contain path traversal sequences.")
    # Only keep the basename — never allow directory components in user filenames
    name = Path(name).name
    if not name or name in {".", ".."}:
        raise PathSecurityError("Invalid filename.")
    return name


def ensure_output_directory(output_directory: str | None = None) -> Path:
    """Resolve and create the output directory."""
    base = Path(output_directory).expanduser() if output_directory else get_output_dir()
    resolved = base.resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def resolve_output_path(
    filename: str | None,
    output_directory: str | None,
    default_extension: str = "",
    overwrite: bool = False,
) -> Path | ToolError:
    """Resolve a safe absolute output path within the output directory."""
    try:
        output_dir = ensure_output_directory(output_directory)

        if filename:
            safe_name = sanitize_filename(filename)
        else:
            ext = default_extension.lstrip(".")
            suffix = f".{ext}" if ext else ""
            safe_name = f"test-file-{uuid.uuid4().hex[:12]}{suffix}"

        target = (output_dir / safe_name).resolve()

        # Ensure target stays within output directory (no traversal via symlinks)
        try:
            target.relative_to(output_dir)
        except ValueError:
            return error_result(
                "Resolved path escapes the output directory.",
                requested=str(target),
                output_directory=str(output_dir),
            )

        if target.exists() and not overwrite:
            return error_result(
                f"File already exists: {target.name}. Set overwrite=true to replace it.",
                path=str(target),
            )

        return target
    except PathSecurityError as exc:
        return error_result(str(exc))
    except OSError as exc:
        return error_result(f"Failed to prepare output path: {exc}")


def validate_existing_path(
    path: str,
    allowed_directories: list[Path] | None = None,
) -> Path | ToolError:
    """Validate that an existing file path is readable and within allowed directories."""
    try:
        resolved = Path(path).expanduser().resolve(strict=True)
    except FileNotFoundError:
        return error_result(f"Source file not found: {path}")
    except OSError as exc:
        return error_result(f"Cannot access source file: {exc}")

    if not resolved.is_file():
        return error_result(f"Source path is not a regular file: {path}")

    if allowed_directories:
        allowed = False
        for directory in allowed_directories:
            try:
                resolved.relative_to(directory.resolve())
                allowed = True
                break
            except ValueError:
                continue
        if not allowed:
            return error_result(
                "Source file must be inside an allowed directory.",
                path=str(resolved),
            )

    return resolved


def is_safe_edge_case_filename(filename: str) -> bool:
    """Check if a filename is safe for the current OS."""
    try:
        # Attempt to create a path — will fail on illegal names on some OSes
        test = Path(filename)
        if test.name != filename:
            return False
        return not UNSAFE_FILENAME_PATTERN.search(filename)
    except (ValueError, OSError):
        return False
