"""Configuration and safety limits for Test Files MCP."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("./test-files-output")

DEFAULT_MAX_FILE_SIZE_MB = 250
DEFAULT_MAX_CSV_ROWS = 1_000_000
DEFAULT_MAX_PDF_PAGES = 1_000
DEFAULT_MAX_IMAGE_DIMENSION = 12_000
DEFAULT_MAX_AUDIO_DURATION_SECONDS = 600

CHUNK_SIZE_BYTES = 1024 * 1024  # 1 MB chunks for streaming writes


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {name}: {raw!r}") from exc


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {name}: {raw!r}") from exc


def get_output_dir() -> Path:
    """Return the configured default output directory."""
    raw = os.environ.get("TEST_FILES_OUTPUT_DIR")
    if raw:
        return Path(raw).expanduser()
    return DEFAULT_OUTPUT_DIR.resolve()


def get_max_file_size_bytes() -> int:
    """Maximum allowed file size in bytes."""
    mb = _env_int("TEST_FILES_MAX_FILE_SIZE_MB", DEFAULT_MAX_FILE_SIZE_MB)
    return mb * 1024 * 1024


def get_max_csv_rows() -> int:
    return _env_int("TEST_FILES_MAX_CSV_ROWS", DEFAULT_MAX_CSV_ROWS)


def get_max_pdf_pages() -> int:
    return _env_int("TEST_FILES_MAX_PDF_PAGES", DEFAULT_MAX_PDF_PAGES)


def get_max_image_dimension() -> int:
    return _env_int("TEST_FILES_MAX_IMAGE_DIMENSION", DEFAULT_MAX_IMAGE_DIMENSION)


def get_max_audio_duration_seconds() -> float:
    return _env_float(
        "TEST_FILES_MAX_AUDIO_DURATION_SECONDS",
        DEFAULT_MAX_AUDIO_DURATION_SECONDS,
    )
