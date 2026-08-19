# Test Files MCP

Generate test files directly from your AI coding assistant.

Need a 20 MB JPEG? A 100,000-row CSV? A corrupted PDF?
Ask your MCP client and Test Files MCP creates it locally.

## Why this exists

Testing file uploads, parsers, validators, and storage limits usually means hunting for sample files or writing one-off scripts. Test Files MCP lets you describe what you need in plain language and get a real file on disk with useful metadata back.

## Features

- **Dummy files** — exact byte sizes (1 byte to GB-scale, within limits)
- **Images** — JPEG, PNG, WEBP, BMP with dimensions, patterns, and approximate target sizes
- **PDFs** — multi-page, blank or with fixture text, approximate target sizes
- **CSV** — streamed generation up to 1M rows
- **JSON** — valid or intentionally malformed fixtures
- **ZIP archives** — empty, flat, or nested
- **WAV audio** — tones or silence at configurable duration
- **Corrupted files** — truncate, bad headers, garbage bytes, wrong extensions
- **Edge-case filenames** — spaces, unicode, long names, hidden files
- **File inspection** — size, MIME type, SHA256, image/audio metadata

## Example prompts

Tell your MCP client things like:

```
Create a 25 MB JPEG

Generate a CSV with 500,000 rows

Create a corrupted PDF

Give me a 30-second WAV

Create an empty ZIP

Generate a weird filename for upload testing
```

## Installation

### With uvx (recommended)

From Git (replace `Zulelee` with your GitHub username or org):

```bash
uvx --from git+https://github.com/Zulelee/test-files-mcp test-files-mcp
```

After publishing to PyPI:

```bash
uvx test-files-mcp
```

### From source

```bash
git clone https://github.com/Zulelee/test-files-mcp
cd test-files-mcp
uv sync
uv run test-files-mcp
```

## Cursor setup

Add to your Cursor MCP settings (`.cursor/mcp.json` or Cursor Settings → MCP):

```json
{
  "mcpServers": {
    "test-files": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Zulelee/test-files-mcp",
        "test-files-mcp"
      ]
    }
  }
}
```

For local development:

```json
{
  "mcpServers": {
    "test-files": {
      "command": "uv",
      "args": ["run", "test-files-mcp"],
      "cwd": "/path/to/test-files-mcp"
    }
  }
}
```

## Claude Desktop setup

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "test-files": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Zulelee/test-files-mcp",
        "test-files-mcp"
      ]
    }
  }
}
```

## Available MCP tools

| Tool | Description |
|------|-------------|
| `create_dummy_file_tool` | Generic file with exact byte size |
| `create_image_tool` | JPEG, PNG, WEBP, BMP images |
| `create_pdf_tool` | Multi-page PDF fixtures |
| `create_csv_tool` | CSV with synthetic rows (streamed) |
| `create_json_tool` | Valid or malformed JSON |
| `create_archive_tool` | ZIP archives |
| `create_audio_tool` | WAV audio (tone or silence) |
| `create_corrupted_file_tool` | Corrupted copy of a file |
| `create_edge_case_filename_tool` | Files with tricky filenames |
| `inspect_file_tool` | Inspect file metadata |

## Configuration

Set environment variables to customize behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_FILES_OUTPUT_DIR` | `./test-files-output/` | Default output directory |
| `TEST_FILES_MAX_FILE_SIZE_MB` | `250` | Maximum file size (MB) |
| `TEST_FILES_MAX_CSV_ROWS` | `1000000` | Maximum CSV rows |
| `TEST_FILES_MAX_PDF_PAGES` | `1000` | Maximum PDF pages |
| `TEST_FILES_MAX_IMAGE_DIMENSION` | `12000` | Max image width/height |
| `TEST_FILES_MAX_AUDIO_DURATION_SECONDS` | `600` | Max audio duration |

Generated files are written to the output directory and returned as **absolute paths**.

## Safety limits

This MCP intentionally generates large files. Requests exceeding configured limits return a clear error — values are never silently clamped.

Example error:

```
Requested file size is 500 MB, but the configured maximum is 250 MB.
Set TEST_FILES_MAX_FILE_SIZE_MB to increase the limit.
```

## Development

```bash
git clone https://github.com/Zulelee/test-files-mcp
cd test-files-mcp
uv sync --group dev
```

### Running tests

```bash
uv run pytest
uv run ruff check src tests
```

### MCP Inspector

```bash
uv run mcp dev src/test_files_mcp/server.py
```

## Contributing

Contributions welcome! Please open an issue or pull request on GitHub.

Suggested topics for the repository:

`mcp`, `model-context-protocol`, `python`, `testing`, `developer-tools`, `test-data`, `fixtures`, `qa`, `cursor`, `claude`, `file-upload`, `open-source`

## License

MIT — see [LICENSE](LICENSE).
