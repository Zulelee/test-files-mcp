---
name: generate-test-files
description: >-
  Generate local test fixtures via Test Files MCP. Use when the user needs dummy
  files, images, PDFs, CSVs, JSON, ZIPs, WAV audio, corrupted files, or
  edge-case filenames for upload testing, QA, parser testing, or validation.
---

# Generate Test Files

Use the **test-files** MCP server tools to create files on disk. Always return the absolute path and metadata from the tool response.

## When to use

- File upload size or type testing
- Parser/validator error handling
- QA fixtures (large CSV, multi-page PDF, oversized images)
- Corrupted or malformed file testing
- Filename edge cases (unicode, spaces, long names)

## Tool selection

| Request | Tool |
|---------|------|
| Exact byte size, random/zeros/text content | `create_dummy_file_tool` |
| JPEG, PNG, WEBP, BMP | `create_image_tool` |
| Multi-page PDF | `create_pdf_tool` |
| CSV rows/columns | `create_csv_tool` |
| Valid or malformed JSON | `create_json_tool` |
| ZIP archive | `create_archive_tool` |
| WAV tone or silence | `create_audio_tool` |
| Corrupted copy of a file | `create_corrupted_file_tool` |
| Tricky filename | `create_edge_case_filename_tool` |
| Inspect existing file | `inspect_file_tool` |

## Defaults

- Output directory: `./test-files-output/` (or `TEST_FILES_OUTPUT_DIR`)
- Do not overwrite existing files unless `overwrite=true`
- Respect safety limits (`TEST_FILES_MAX_*` env vars)

## Examples

- "Create a 20 MB JPEG" → `create_image_tool` with `target_size_mb=20`, `format="jpeg"`
- "CSV with 100,000 rows" → `create_csv_tool` with `rows=100000`
- "Corrupted PDF" → `create_corrupted_file_tool` with `file_type="pdf"`
- "30-second silent WAV" → `create_audio_tool` with `duration_seconds=30`, `silence=true`
