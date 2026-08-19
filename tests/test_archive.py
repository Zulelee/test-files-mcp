"""Tests for ZIP archive generation."""

from __future__ import annotations

import zipfile
from pathlib import Path

from test_files_mcp.generators.archive import create_archive


def test_empty_zip(output_dir: Path) -> None:
    result = create_archive(
        filename="empty.zip",
        empty=True,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    with zipfile.ZipFile(result.path) as zf:
        assert len(zf.namelist()) == 0


def test_file_count(output_dir: Path) -> None:
    result = create_archive(
        filename="files.zip",
        files=20,
        output_directory=str(output_dir),
        overwrite=True,
        seed=1,
    )
    assert result.success is True
    assert result.details["files"] == 20


def test_nested_archive(output_dir: Path) -> None:
    result = create_archive(
        filename="nested.zip",
        files=10,
        nested=True,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    with zipfile.ZipFile(result.path) as zf:
        names = zf.namelist()
        assert any("/" in n for n in names)
