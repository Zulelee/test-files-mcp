"""WAV audio file generator."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from test_files_mcp.config import get_max_audio_duration_seconds
from test_files_mcp.models import ToolError, ToolSuccess, error_result, success_result
from test_files_mcp.utils.paths import resolve_output_path


def create_audio(
    filename: str | None = None,
    duration_seconds: float = 5.0,
    sample_rate: int = 44100,
    channels: int = 1,
    tone_hz: float = 440.0,
    silence: bool = False,
    output_directory: str | None = None,
    overwrite: bool = False,
) -> ToolSuccess | ToolError:
    """Generate a WAV audio test fixture."""
    max_duration = get_max_audio_duration_seconds()
    if duration_seconds <= 0:
        return error_result("Duration must be positive.", requested=duration_seconds)
    if duration_seconds > max_duration:
        return error_result(
            f"Requested duration of {duration_seconds}s exceeds configured maximum "
            f"of {max_duration}s. Set TEST_FILES_MAX_AUDIO_DURATION_SECONDS to increase.",
            requested=duration_seconds,
            maximum=max_duration,
        )
    if channels not in (1, 2):
        return error_result("Channels must be 1 or 2.", requested=channels)
    if sample_rate < 8000:
        return error_result("Sample rate must be at least 8000.", requested=sample_rate)

    path_result = resolve_output_path(
        filename, output_directory, default_extension="wav", overwrite=overwrite
    )
    if isinstance(path_result, ToolError):
        return path_result

    path: Path = path_result
    num_frames = int(duration_seconds * sample_rate)

    try:
        with wave.open(str(path), "w") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)

            for frame_idx in range(num_frames):
                if silence:
                    sample = 0
                else:
                    t = frame_idx / sample_rate
                    sample = int(32767 * 0.5 * math.sin(2 * math.pi * tone_hz * t))
                frame_data = struct.pack("<h", sample)
                if channels == 2:
                    frame_data += frame_data
                wf.writeframes(frame_data)
    except OSError as exc:
        return error_result(f"Failed to write WAV: {exc}")

    actual_size = path.stat().st_size
    return success_result(
        path=str(path.resolve()),
        filename=path.name,
        file_type="audio/wav",
        size_bytes=actual_size,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        channels=channels,
        tone_hz=None if silence else tone_hz,
        silence=silence,
    )
