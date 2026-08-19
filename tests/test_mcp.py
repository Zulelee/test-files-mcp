"""MCP integration tests using in-memory client."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from mcp import Client

from test_files_mcp.server import mcp


@pytest.fixture
def client():
    return Client(mcp)


def _tool_data(result: Any) -> dict:
    """Extract tool result from MCP structured_content."""
    content = result.structured_content
    if content and "result" in content:
        return content["result"]
    return content or {}


async def test_list_tools(client: Client) -> None:
    async with client:
        result = await client.list_tools()
        tool_names = {t.name for t in result.tools}
        expected = {
            "create_dummy_file_tool",
            "create_image_tool",
            "create_pdf_tool",
            "create_csv_tool",
            "create_json_tool",
            "create_archive_tool",
            "create_audio_tool",
            "create_corrupted_file_tool",
            "create_edge_case_filename_tool",
            "inspect_file_tool",
        }
        assert expected.issubset(tool_names)


async def test_create_dummy_file_tool(client: Client, output_dir: Path) -> None:
    async with client:
        result = await client.call_tool(
            "create_dummy_file_tool",
            {
                "filename": "mcp-test.bin",
                "size_bytes": 512,
                "output_directory": str(output_dir),
                "overwrite": True,
            },
        )
        assert result.is_error is False
        assert result.structured_content is not None
        data = _tool_data(result)
        assert data["success"] is True
        assert data["size_bytes"] == 512
        assert Path(data["path"]).exists()


async def test_create_image_tool(client: Client, output_dir: Path) -> None:
    async with client:
        result = await client.call_tool(
            "create_image_tool",
            {
                "filename": "mcp.png",
                "width": 100,
                "height": 100,
                "output_directory": str(output_dir),
                "overwrite": True,
            },
        )
        assert result.is_error is False
        data = _tool_data(result)
        assert data["success"] is True
        assert Path(data["path"]).exists()


async def test_error_on_size_limit(client: Client, output_dir: Path, monkeypatch) -> None:
    monkeypatch.setenv("TEST_FILES_MAX_FILE_SIZE_MB", "1")
    async with client:
        result = await client.call_tool(
            "create_dummy_file_tool",
            {
                "size_mb": 5,
                "output_directory": str(output_dir),
            },
        )
        assert result.is_error is False
        data = _tool_data(result)
        assert data["success"] is False
        assert "maximum" in data["error"].lower()


async def test_inspect_file_tool(client: Client, output_dir: Path) -> None:
    async with client:
        created = await client.call_tool(
            "create_dummy_file_tool",
            {
                "filename": "inspect-me.bin",
                "size_bytes": 256,
                "output_directory": str(output_dir),
                "overwrite": True,
            },
        )
        path = _tool_data(created)["path"]
        result = await client.call_tool("inspect_file_tool", {"path": path})
        assert result.is_error is False
        data = _tool_data(result)
        assert data["success"] is True
        assert data["size_bytes"] == 256
        assert "sha256" in data["details"]


async def test_edge_case_filename(client: Client, output_dir: Path) -> None:
    async with client:
        result = await client.call_tool(
            "create_edge_case_filename_tool",
            {
                "case": "unicode",
                "output_directory": str(output_dir),
                "overwrite": True,
            },
        )
        assert result.is_error is False
        data = _tool_data(result)
        assert data["success"] is True
        assert Path(data["path"]).exists()
