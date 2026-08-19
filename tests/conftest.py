"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def output_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide an isolated output directory for each test."""
    out = tmp_path / "test-output"
    out.mkdir()
    monkeypatch.setenv("TEST_FILES_OUTPUT_DIR", str(out))
    # Reset high limits for most tests
    monkeypatch.setenv("TEST_FILES_MAX_FILE_SIZE_MB", "250")
    monkeypatch.setenv("TEST_FILES_MAX_CSV_ROWS", "1000000")
    monkeypatch.setenv("TEST_FILES_MAX_PDF_PAGES", "1000")
    monkeypatch.setenv("TEST_FILES_MAX_IMAGE_DIMENSION", "12000")
    monkeypatch.setenv("TEST_FILES_MAX_AUDIO_DURATION_SECONDS", "600")
    return out
