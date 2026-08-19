"""Tests for file corruption."""

from __future__ import annotations

from pathlib import Path

from test_files_mcp.corruption.corrupt import create_corrupted_file
from test_files_mcp.generators.binary import create_dummy_file


def test_original_unchanged(output_dir: Path) -> None:
    source = create_dummy_file(
        filename="source.bin",
        size_bytes=1000,
        seed=1,
        output_directory=str(output_dir),
        overwrite=True,
    )
    original_data = Path(source.path).read_bytes()

    result = create_corrupted_file(
        source_path=source.path,
        corruption="truncate",
        severity=0.5,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert Path(source.path).read_bytes() == original_data


def test_corrupted_differs(output_dir: Path) -> None:
    source = create_dummy_file(
        filename="source2.bin",
        size_bytes=500,
        seed=2,
        output_directory=str(output_dir),
        overwrite=True,
    )
    result = create_corrupted_file(
        source_path=source.path,
        corruption="random_bytes",
        severity=0.8,
        seed=10,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert Path(result.path).read_bytes() != Path(source.path).read_bytes()


def test_truncate(output_dir: Path) -> None:
    result = create_corrupted_file(
        file_type="generic",
        corruption="truncate",
        severity=0.3,
        seed=5,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert "truncated_to_bytes" in result.details


def test_append_garbage(output_dir: Path) -> None:
    result = create_corrupted_file(
        file_type="jpeg",
        corruption="append_garbage",
        severity=0.5,
        seed=3,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["corruption"] == "append_garbage"
