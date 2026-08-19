#!/usr/bin/env python3
"""Generate one-click MCP install links for README badges."""

from __future__ import annotations

import base64
import json
from pathlib import Path

REPO = "Zulelee/test-files-mcp"
SERVER_NAME = "test-files"

CURSOR_CONFIG = {
    "command": "uvx",
    "args": [
        "--from",
        f"git+https://github.com/{REPO}",
        "test-files-mcp",
    ],
}

CLAUDE_CONFIG = {
    "mcpServers": {
        SERVER_NAME: {
            "command": "uvx",
            "args": [
                "--from",
                f"git+https://github.com/{REPO}",
                "test-files-mcp",
            ],
        }
    }
}


def cursor_install_url() -> str:
    encoded = base64.b64encode(json.dumps(CURSOR_CONFIG, separators=(",", ":")).encode()).decode()
    return (
        f"https://cursor.com/install-mcp?name={SERVER_NAME}&config={encoded}"
    )


def cursor_deeplink() -> str:
    encoded = base64.b64encode(json.dumps(CURSOR_CONFIG, separators=(",", ":")).encode()).decode()
    return f"cursor://anysphere.cursor-deeplink/mcp/install?name={SERVER_NAME}&config={encoded}"


def mcpb_download_url(branch: str = "main") -> str:
    return f"https://github.com/{REPO}/raw/{branch}/dist/test-files-mcp.mcpb"


def readme_badges_section() -> str:
    cursor_url = cursor_install_url()
    mcpb_url = mcpb_download_url()
    return f"""## One-click install

[![Add to Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)]({cursor_url})
[![Add to Claude](https://img.shields.io/badge/Claude-Install%20Extension-D97757?style=for-the-badge&logo=anthropic&logoColor=white)]({mcpb_url})

| Client | What happens when you click |
|--------|----------------------------|
| **Cursor** | Opens Cursor and prompts you to add the MCP server to your config |
| **Claude Desktop** | Downloads `test-files-mcp.mcpb` — double-click it to install in Claude |

> Claude Desktop does not support URL-based MCP config injection. The `.mcpb` bundle is the official [one-click install format](https://claude.com/docs/connectors/building/mcpb) for local MCP servers.

<details>
<summary>Manual Claude Desktop config (JSON)</summary>

Open **Settings → Developer → Edit Config** and add:

```json
{json.dumps(CLAUDE_CONFIG, indent=2)}
```

</details>
"""


def main() -> None:
    print(readme_badges_section())
    print("\n---\n")
    print("Cursor deeplink:", cursor_deeplink())


if __name__ == "__main__":
    main()
