"""CSV file generator."""

from __future__ import annotations

import csv
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from test_files_mcp.config import get_max_csv_rows
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path

DEFAULT_HEADERS = ["id", "name", "email", "amount", "created_at"]


def _generate_headers(columns: int, headers: list[str] | None) -> list[str]:
    if headers:
        if len(headers) < columns:
            return headers + [f"column_{i}" for i in range(len(headers) + 1, columns + 1)]
        return headers[:columns]
    if columns <= len(DEFAULT_HEADERS):
        return DEFAULT_HEADERS[:columns]
    return DEFAULT_HEADERS + [f"column_{i}" for i in range(len(DEFAULT_HEADERS) + 1, columns + 1)]


def _generate_row(row_id: int, fieldnames: list[str], rng: random.Random) -> dict[str, str]:
    base_date = datetime(2024, 1, 1, tzinfo=UTC)
    row: dict[str, str] = {}
    for field in fieldnames:
        if field == "id":
            row[field] = str(row_id)
        elif field == "name":
            row[field] = f"Test User {row_id}"
        elif field == "email":
            row[field] = f"user{row_id}@example.test"
        elif field == "amount":
            row[field] = f"{rng.uniform(1, 9999):.2f}"
        elif field == "created_at":
            row[field] = (base_date + timedelta(days=row_id % 365)).isoformat()
        elif field.startswith("column_"):
            row[field] = f"value_{row_id}_{field}"
        else:
            row[field] = f"{field}_{row_id}"
    return row


def create_csv(
    filename: str | None = None,
    rows: int = 10,
    columns: int = 5,
    headers: list[str] | None = None,
    delimiter: str = ",",
    include_header: bool = True,
    encoding: str = "utf-8",
    seed: int | None = None,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a CSV test fixture, streaming rows to disk."""
    max_rows = get_max_csv_rows()
    if rows < 0:
        return error_result("Row count must be non-negative.", requested=rows)
    if rows > max_rows:
        return error_result(
            f"Requested {rows} rows exceeds configured maximum of {max_rows}. "
            f"Set TEST_FILES_MAX_CSV_ROWS to increase the limit.",
            requested=rows,
            maximum=max_rows,
        )
    if columns < 1:
        return error_result("Column count must be at least 1.", requested=columns)

    path_result = resolve_output_path(
        filename, output_directory, default_extension="csv", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    fieldnames = _generate_headers(columns, headers)
    rng = random.Random(seed)
    path: Path = path_result

    try:
        with path.open("w", encoding=encoding, newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=delimiter)
            if include_header:
                writer.writeheader()
            for row_id in range(1, rows + 1):
                writer.writerow(_generate_row(row_id, fieldnames, rng))
    except OSError as exc:
        return error_result(f"Failed to write CSV: {exc}")

    actual_size = path.stat().st_size
    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="text/csv",
        size_bytes=actual_size,
        rows=rows,
        columns=columns,
        delimiter=delimiter,
        encoding=encoding,
        include_header=include_header,
        seed=seed,
    )
