"""Tests for path security utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from test_files_mcp.generators.binary import create_dummy_file
from test_files_mcp.utils.paths import PathSecurityError, resolve_output_path, sanitize_filename


def test_path_traversal_blocked(output_dir: Path) -> None:
    result = resolve_output_path(
        filename="../../bad.txt",
        output_directory=str(output_dir),
    )
    # Traversal sequences in filenames are rejected
    assert hasattr(result, "success")
    assert result.success is False


def test_traversal_in_filename_rejected() -> None:
    with pytest.raises(PathSecurityError):
        sanitize_filename("../secret.txt")


def test_overwrite_protection(output_dir: Path) -> None:
    create_dummy_file(
        filename="protected.bin",
        size_bytes=10,
        output_directory=str(output_dir),
        overwrite=True,
    )
    result = create_dummy_file(
        filename="protected.bin",
        size_bytes=20,
        output_directory=str(output_dir),
        overwrite=False,
    )
    assert result.success is False
    assert "already exists" in result.error.lower()


def test_overwrite_allowed(output_dir: Path) -> None:
    create_dummy_file(
        filename="replace.bin",
        size_bytes=10,
        output_directory=str(output_dir),
        overwrite=True,
    )
    result = create_dummy_file(
        filename="replace.bin",
        size_bytes=50,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.size_bytes == 50
