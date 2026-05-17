# arxiv-mcp

A lightweight [Model Context Protocol](https://modelcontextprotocol.io) server that gives an LLM the ability to search and explore arXiv papers directly in conversation.

## What it does

Instead of copy-pasting paper IDs or abstracts into your chat, the LLM can search arXiv, retrieve full paper details, and find related work on its own.

**Available tools:**

- `search_papers(query, max_results)` — full-text search across arXiv
- `get_paper(arxiv_id)` — fetch full metadata and abstract for a specific paper
- `find_related(arxiv_id)` — discover related work based on a paper's title

## How it works

The server is a single Python file using [FastMCP](https://github.com/jlowin/fastmcp), which handles all the MCP protocol plumbing. Each function decorated with `@mcp.tool()` becomes a tool your AI assistant can call. Dependencies are declared inline using uv's [script metadata](https://docs.astral.sh/uv/guides/scripts/#declaring-script-dependencies) format, and therefore no `requirements.txt` or `venv` are needed.

On startup, the agent launches the server as a background process over stdio. It reads the tool definitions (names, descriptions, parameter types) and decides autonomously when and how to call them based on your message.

## License

MIT
