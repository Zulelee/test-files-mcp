"""Pydantic models for structured tool responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolError(BaseModel):
    """Structured error response returned by generation tools."""

    success: bool = False
    error: str
    details: dict[str, Any] = Field(default_factory=dict)


class ToolSuccess(BaseModel):
    """Structured success response returned by generation tools."""

    success: bool = True
    path: str
    filename: str
    file_type: str
    size_bytes: int
    details: dict[str, Any] = Field(default_factory=dict)


ToolResult = ToolSuccess | ToolError


def success_result(
    path: str,
    filename: str,
    file_type: str,
    size_bytes: int,
    **details: Any,
) -> ToolSuccess:
    return ToolSuccess(
        path=path,
        filename=filename,
        file_type=file_type,
        size_bytes=size_bytes,
        details=details,
    )


def error_result(error: str, **details: Any) -> ToolError:
    return ToolError(error=error, details=details)
