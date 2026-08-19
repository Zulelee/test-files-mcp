"""Tests for binary/dummy file generation."""

from __future__ import annotations

from pathlib import Path

from test_files_mcp.generators.binary import create_dummy_file


def test_exact_byte_size(output_dir: Path) -> None:
    result = create_dummy_file(
        filename="exact.bin",
        size_bytes=1024,
        content="random",
        seed=42,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.size_bytes == 1024
    assert Path(result.path).exists()


def test_zero_byte_file(output_dir: Path) -> None:
    result = create_dummy_file(
        filename="empty.bin",
        size_bytes=0,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.size_bytes == 0
    assert Path(result.path).stat().st_size == 0


def test_chunked_large_file(output_dir: Path) -> None:
    result = create_dummy_file(
        filename="large.bin",
        size_kb=512,
        content="zeros",
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.size_bytes == 512 * 1024
    assert Path(result.path).stat().st_size == 512 * 1024


def test_text_content(output_dir: Path) -> None:
    result = create_dummy_file(
        filename="text.bin",
        size_bytes=100,
        content="text",
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    data = Path(result.path).read_bytes()
    assert b"Test Files MCP" in data
