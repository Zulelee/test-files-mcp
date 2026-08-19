---
description: Generate a test file fixture using Test Files MCP. Pass a description as the argument (e.g. "20 MB JPEG", "100k row CSV", "corrupted PDF").
---

# Generate Test File

Create a test fixture using the **test-files** MCP server based on: **$ARGUMENTS**

## Steps

1. Parse the user's request from `$ARGUMENTS` (file type, size, count, corruption, etc.).
2. Select the appropriate MCP tool:
   - Size-only file → `create_dummy_file_tool`
   - Image → `create_image_tool`
   - PDF → `create_pdf_tool`
   - CSV → `create_csv_tool`
   - JSON → `create_json_tool`
   - ZIP → `create_archive_tool`
   - WAV → `create_audio_tool`
   - Corrupted → `create_corrupted_file_tool`
   - Weird filename → `create_edge_case_filename_tool`
3. Call the tool and confirm the file exists at the returned absolute path.
4. Summarize: path, size, and key metadata.

If the request is ambiguous, ask one clarifying question before generating.
