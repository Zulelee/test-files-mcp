"""Image file generator."""

from __future__ import annotations

import io
import random
from pathlib import Path

from PIL import Image, ImageDraw

from test_files_mcp.config import get_max_image_dimension
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path
from test_files_mcp.utils.sizes import resolve_size_bytes

FORMAT_MAP = {
    "jpeg": ("JPEG", ".jpg", "image/jpeg"),
    "jpg": ("JPEG", ".jpg", "image/jpeg"),
    "png": ("PNG", ".png", "image/png"),
    "webp": ("WEBP", ".webp", "image/webp"),
    "bmp": ("BMP", ".bmp", "image/bmp"),
}


def _parse_color(background: str) -> tuple[int, int, int]:
    background = background.strip().lstrip("#")
    if len(background) == 6:
        return (
            int(background[0:2], 16),
            int(background[2:4], 16),
            int(background[4:6], 16),
        )
    return (128, 128, 128)


def _make_pattern_image(
    width: int,
    height: int,
    pattern: str,
    background: str,
    rng: random.Random,
) -> Image.Image:
    color = _parse_color(background)
    img = Image.new("RGB", (width, height), color)

    if pattern == "solid":
        return img

    if pattern == "noise":
        pixels = img.load()
        assert pixels is not None
        for y in range(height):
            for x in range(0, width, 4):
                pixels[x, y] = (
                    rng.randint(0, 255),
                    rng.randint(0, 255),
                    rng.randint(0, 255),
                )
        return img

    if pattern == "gradient":
        draw = ImageDraw.Draw(img)
        for y in range(height):
            ratio = y / max(height - 1, 1)
            r = int(color[0] * (1 - ratio) + 255 * ratio)
            g = int(color[1] * (1 - ratio) + 128 * ratio)
            b = int(color[2] * (1 - ratio) + 64 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        return img

    if pattern == "checkerboard":
        draw = ImageDraw.Draw(img)
        square = max(min(width, height) // 20, 8)
        for y in range(0, height, square):
            for x in range(0, width, square):
                if ((x // square) + (y // square)) % 2 == 0:
                    draw.rectangle([x, y, x + square, y + square], fill=(200, 200, 200))
        return img

    return img


def _save_image(
    img: Image.Image,
    pil_format: str,
    quality: int,
) -> bytes:
    buf = io.BytesIO()
    save_kwargs: dict = {"format": pil_format}
    if pil_format in {"JPEG", "WEBP"}:
        save_kwargs["quality"] = quality
    img.save(buf, **save_kwargs)
    return buf.getvalue()


def create_image(
    filename: str | None = None,
    format: str = "png",
    width: int = 1024,
    height: int = 1024,
    target_size_kb: float | None = None,
    target_size_mb: float | None = None,
    background: str = "808080",
    pattern: str = "noise",
    quality: int = 85,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a test image file."""
    fmt = format.lower()
    if fmt not in FORMAT_MAP:
        return error_result(
            f"Unsupported image format: {format}",
            supported=list(FORMAT_MAP.keys()),
        )

    max_dim = get_max_image_dimension()
    if width > max_dim or height > max_dim:
        return error_result(
            "Requested image dimensions exceed configured maximum.",
            requested_width=width,
            requested_height=height,
            maximum=max_dim,
        )

    if width < 1 or height < 1:
        return error_result("Width and height must be at least 1.")

    # Resolve target size if requested
    target_bytes: int | None = None
    if target_size_kb is not None or target_size_mb is not None:
        resolved = resolve_size_bytes(None, target_size_kb, target_size_mb)
        if isinstance(resolved, ToolError):
            return resolved
        target_bytes = resolved

    pil_format, default_ext, mime = FORMAT_MAP[fmt]
    if filename is None:
        filename = f"test-image{default_ext}"

    path_result = resolve_output_path(
        filename, output_directory, default_extension=default_ext.lstrip("."), overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    rng = random.Random(seed)
    img = _make_pattern_image(width, height, pattern, background, rng)

    padded = False
    current_quality = quality

    if target_bytes is not None:
        # Binary search quality for JPEG/WEBP
        if pil_format in {"JPEG", "WEBP"}:
            low, high = 1, 95
            best_data = _save_image(img, pil_format, current_quality)
            while low <= high:
                mid = (low + high) // 2
                data = _save_image(img, pil_format, mid)
                if len(data) <= target_bytes:
                    best_data = data
                    current_quality = mid
                    low = mid + 1
                else:
                    high = mid - 1
            image_data = best_data
        else:
            image_data = _save_image(img, pil_format, current_quality)

        if len(image_data) < target_bytes:
            padding_needed = target_bytes - len(image_data)
            # For large padding, append trailing bytes (most decoders still read the image)
            if padding_needed > 65500:
                image_data = image_data + b"\x00" * padding_needed
                padded = True
            elif pil_format == "JPEG" and image_data[:2] == b"\xff\xd8":
                eoi = image_data.rfind(b"\xff\xd9")
                if eoi > 0 and padding_needed >= 4:
                    segment_len = padding_needed - 2
                    pad = (
                        b"\xff\xe0"
                        + segment_len.to_bytes(2, "big")
                        + b"\x00" * (segment_len - 2)
                    )
                    image_data = image_data[:eoi] + pad + image_data[eoi:]
                    padded = True
                else:
                    image_data = image_data + b"\x00" * padding_needed
                    padded = True
            else:
                image_data = image_data + b"\x00" * padding_needed
                padded = True
    else:
        image_data = _save_image(img, pil_format, current_quality)

    path: Path = path_result
    try:
        path.write_bytes(image_data)
    except OSError as exc:
        return error_result(f"Failed to write image: {exc}")

    actual_size = path.stat().st_size
    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type=mime,
        size_bytes=actual_size,
        width=width,
        height=height,
        format=fmt,
        pattern=pattern,
        quality=current_quality,
        target_size_bytes=target_bytes,
        difference_bytes=(actual_size - target_bytes) if target_bytes else None,
        padded=padded,
        seed=seed,
    )
