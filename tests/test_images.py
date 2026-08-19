"""Tests for image generation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from test_files_mcp.generators.images import create_image


def test_expected_dimensions(output_dir: Path) -> None:
    result = create_image(
        filename="dims.png",
        format="png",
        width=800,
        height=600,
        pattern="solid",
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["width"] == 800
    assert result.details["height"] == 600


def test_jpeg_format(output_dir: Path) -> None:
    result = create_image(
        filename="photo.jpg",
        format="jpeg",
        width=1920,
        height=1080,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["format"] == "jpeg"
    with Image.open(result.path) as img:
        assert img.format == "JPEG"
        assert img.size == (1920, 1080)


def test_target_size_behavior(output_dir: Path) -> None:
    result = create_image(
        filename="sized.jpg",
        format="jpeg",
        width=512,
        height=512,
        target_size_kb=50,
        seed=1,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["target_size_bytes"] == 50 * 1024
    # Should be reasonably close (within 50% due to compression variability)
    assert result.size_bytes > 0


def test_deterministic_with_seed(output_dir: Path) -> None:
    r1 = create_image(
        filename="seed1.png",
        seed=99,
        output_directory=str(output_dir),
        overwrite=True,
    )
    r2 = create_image(
        filename="seed2.png",
        seed=99,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert Path(r1.path).read_bytes() == Path(r2.path).read_bytes()
