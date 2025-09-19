# Claude eXtend (cx)

A CLI tool for managing Model Context Protocol (MCP) server connections with Claude Code.

Claude eXtend allows you to easily link, unlink, and manage MCP servers that extend Claude Code's capabilities. It assumes MCP servers are already installed on your system and helps you configure which ones are active in Claude Code.

## Quick Start

Run `cx` instantly with `uvx` directly from GitHub (no installation required):

```bash
uvx --from git+https://github.com/cearley/claude-extend cx
```

Or install locally from GitHub:

```bash
uv tool install git+https://github.com/cearley/claude-extend
```

## Usage

```bash
cx                 # Show help and available commands
cx list           # List connected MCP servers
cx link <server>  # Link an MCP server to Claude Code
cx unlink <server> # Unlink an MCP server from Claude Code
```

## What are MCP Servers?

Model Context Protocol (MCP) servers extend Claude Code's capabilities by providing additional tools and context. Examples include:

- File system access tools
- Database connection tools
- API integration tools
- Development environment tools

Claude eXtend helps you manage which of these installed servers are active in your Claude Code setup.

## Requirements

- Python 3.8+
- `uv` package manager (for `uvx` usage)

## Development

See [CLAUDE.md](CLAUDE.md) for development guidance.

## License

MIT