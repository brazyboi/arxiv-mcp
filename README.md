# arxiv-mcp

A lightweight [Model Context Protocol](https://modelcontextprotocol.io) server that gives Claude (and any other MCP-compatible client) the ability to search and explore arXiv papers directly in conversation.

## What it does

Instead of copy-pasting paper IDs or abstracts into your chat, your AI assistant can search arXiv, retrieve full paper details, and find related work on its own.

**Available tools:**

- `search_papers(query, max_results)` — full-text search across arXiv
- `get_paper(arxiv_id)` — fetch full metadata and abstract for a specific paper
- `find_related(arxiv_id)` — discover related work based on a paper's title

## Requirements

- [uv](https://docs.astral.sh/uv/) — no other setup needed, dependencies are managed automatically

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/brazyboi/arxiv-mcp.git
cd arxiv-mcp
```

**2. Test the server runs**

```bash
uv run server.py
```

You should see a blank prompt with the cursor waiting, no errors.

**3. Add to your config**

If you are using Claude, open your Claude Desktop config file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the following, replacing the path with your actual absolute path:

```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/arxiv-mcp/arxiv_server.py"]
    }
  }
}
```

It's usually similar for any other MCP-compatible client.

**4. Restart Your Client**

Fully quit and reopen Claude or your client. You should see `search_papers`, `get_paper`, and `find_related` listed when you click the tools (hammer) icon in the chat input.

## Usage

Just talk to your client naturally:

> *"Find me recent papers on speculative decoding"*

> *"Get the full abstract for 2303.08774"*

> *"What work is related to that last paper?"*

It will call the appropriate tools automatically and present the results conversationally.

## How it works

The server is a single Python file using [FastMCP](https://github.com/jlowin/fastmcp), which handles all the MCP protocol plumbing. Each function decorated with `@mcp.tool()` becomes a tool your AI assistant can call. Dependencies are declared inline using uv's [script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) format, and therefore no `requirements.txt` or `venv` are needed.

When Claude starts, it launches the server as a background process over stdio. Claude reads the tool definitions (names, descriptions, parameter types) and decides autonomously when and how to call them based on your message.

## License

MIT
