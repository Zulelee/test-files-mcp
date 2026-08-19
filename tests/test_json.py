"""Tests for JSON generation."""

from __future__ import annotations

import json
from pathlib import Path

from test_files_mcp.generators.json import create_json


def test_valid_json(output_dir: Path) -> None:
    result = create_json(
        filename="valid.json",
        items=3,
        output_directory=str(output_dir),
        overwrite=True,
        seed=1,
    )
    assert result.success is True
    data = json.loads(Path(result.path).read_text())
    assert len(data) == 3


def test_malformed_json(output_dir: Path) -> None:
    result = create_json(
        filename="bad.json",
        items=5,
        malformed=True,
        output_directory=str(output_dir),
        overwrite=True,
        seed=42,
    )
    assert result.success is True
    assert result.details["malformed"] is True
    assert "corruption_type" in result.details
    with Path(result.path).open() as fh, __import__("pytest").raises(json.JSONDecodeError):
        json.load(fh)
