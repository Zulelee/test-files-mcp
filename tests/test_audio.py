"""Tests for WAV audio generation."""

from __future__ import annotations

import wave
from pathlib import Path

from test_files_mcp.generators.audio import create_audio


def test_duration(output_dir: Path) -> None:
    result = create_audio(
        filename="tone.wav",
        duration_seconds=2.0,
        sample_rate=44100,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    with wave.open(result.path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / rate
    assert abs(duration - 2.0) < 0.1


def test_silent_wav(output_dir: Path) -> None:
    result = create_audio(
        filename="silent.wav",
        duration_seconds=1.0,
        silence=True,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    assert result.details["silence"] is True


def test_stereo(output_dir: Path) -> None:
    result = create_audio(
        filename="stereo.wav",
        duration_seconds=0.5,
        channels=2,
        output_directory=str(output_dir),
        overwrite=True,
    )
    assert result.success is True
    with wave.open(result.path, "rb") as wf:
        assert wf.getnchannels() == 2
        assert wf.getframerate() == 44100
