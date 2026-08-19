"""Tests for CSV generation."""

from __future__ import annotations

import csv
from pathlib import Path

from test_files_mcp.generators.csv import create_csv


def test_row_count(output_dir: Path) -> None:
    result = create_csv(
        filename="rows.csv",
        rows=100,
        columns=3,
        output_directory=str(output_dir),
        overwrite=True,
        seed=1,
    )
    assert result.success is True
    with Path(result.path).open() as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    assert len(rows) == 101  # header + 100 data rows


def test_no_header(output_dir: Path) -> None:
    result = create_csv(
        filename="noheader.csv",
        rows=5,
        include_header=False,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    with Path(result.path).open() as fh:
        rows = list(csv.reader(fh))
    assert len(rows) == 5


def test_custom_delimiter(output_dir: Path) -> None:
    result = create_csv(
        filename="pipe.csv",
        rows=3,
        delimiter="|",
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    content = Path(result.path).read_text()
    assert "|" in content
    assert "," not in content.split("\n")[0]


def test_large_csv_streaming(output_dir: Path) -> None:
    result = create_csv(
        filename="large.csv",
        rows=10_000,
        output_directory=str(output_dir),
        overwrite=True,
        seed=7,
    )
    assert result.success is True
    assert result.details["rows"] == 10_000
    assert Path(result.path).stat().st_size > 0
