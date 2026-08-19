"""File inspection and MIME type utilities."""

from __future__ import annotations

import hashlib
import mimetypes
import wave
from pathlib import Path
from typing import Any

from PIL import Image

from test_files_mcp.models import ToolError, ToolSuccess, success_result
from test_files_mcp.utils.paths import validate_existing_path
from test_files_mcp.utils.sizes import format_bytes


def guess_mime_type(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_file(path: str) -> ToolSuccess | ToolError:
    """Inspect a file and return metadata."""
    resolved = validate_existing_path(path)
    if isinstance(resolved, ToolError):
        return resolved

    size = resolved.stat().st_size
    file_meta = format_bytes(size)
    details: dict[str, Any] = {
        "sha256": sha256_file(resolved),
        "exists": True,
    }

    mime = guess_mime_type(resolved)
    ext = resolved.suffix.lower()

    if mime.startswith("image/") or ext in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}:
        try:
            with Image.open(resolved) as img:
                details["width"] = img.width
                details["height"] = img.height
                details["format"] = img.format
        except Exception:
            pass

    if ext == ".wav" or mime == "audio/wav":
        try:
            with wave.open(str(resolved), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                details["sample_rate"] = rate
                details["channels"] = wf.getnchannels()
                details["duration"] = round(frames / rate, 3) if rate else 0
        except Exception:
            pass

    return success_result(
        path=str(resolved),
        filename=resolved.name,
        file_type=mime,
        size_bytes=size,
        size_kb=file_meta["size_kb"],
        size_mb=file_meta["size_mb"],
        **details,
    )
