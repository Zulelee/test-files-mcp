"""JSON file generator."""

from __future__ import annotations

import json
import random
from pathlib import Path

from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path

MALFORMED_VARIANTS = [
    "missing_closing_bracket",
    "trailing_comma",
    "unquoted_key",
    "truncated",
]


def _build_valid_json(items: int, depth: int, rng: random.Random) -> list | dict:
    records = [
        {
            "id": i,
            "name": f"Test Item {i}",
            "active": rng.choice([True, False]),
        }
        for i in range(1, items + 1)
    ]
    if depth <= 1:
        return records

    return {
        "meta": {"generated_by": "test-files-mcp", "depth": depth},
        "items": records,
        "nested": _build_valid_json(min(items, 3), depth - 1, rng) if depth > 1 else [],
    }


def _build_malformed_json(items: int, rng: random.Random) -> tuple[str, str]:
    valid = _build_valid_json(items, 1, rng)
    text = json.dumps(valid, indent=2)

    variant = rng.choice(MALFORMED_VARIANTS)

    if variant == "missing_closing_bracket":
        # Remove last closing bracket
        idx = text.rfind("]")
        if idx == -1:
            idx = text.rfind("}")
        text = text[:idx] if idx > 0 else text
    elif variant == "trailing_comma":
        text = text.replace("\n]", ",\n]")
    elif variant == "unquoted_key":
        text = text.replace('"id"', "id", 1)
    elif variant == "truncated":
        text = text[: max(len(text) // 2, 10)]

    return text, variant


def create_json(
    filename: str | None = None,
    items: int = 5,
    depth: int = 1,
    pretty: bool = True,
    malformed: bool = False,
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a JSON test fixture."""
    if items < 0:
        return error_result("Item count must be non-negative.", requested=items)
    if depth < 1:
        return error_result("Depth must be at least 1.", requested=depth)

    path_result = resolve_output_path(
        filename, output_directory, default_extension="json", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    rng = random.Random(seed)
    corruption_type: str | None = None

    if malformed:
        text, corruption_type = _build_malformed_json(items, rng)
    else:
        data = _build_valid_json(items, depth, rng)
        text = json.dumps(data, indent=2 if pretty else None)

    path: Path = path_result
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        return error_result(f"Failed to write JSON: {exc}")

    actual_size = path.stat().st_size
    details: dict = {
        "items": items,
        "depth": depth,
        "pretty": pretty,
        "malformed": malformed,
        "seed": seed,
    }
    if corruption_type:
        details["corruption_type"] = corruption_type

    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="application/json",
        size_bytes=actual_size,
        **details,
    )
