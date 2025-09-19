# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude eXtend (cx)** - A Python command-line tool for managing which Model Context Protocol (MCP) servers are connected to Claude Code. This tool allows users to link, unlink, and list MCP servers that are already installed on their system but need to be configured with Claude Code.

## Development Environment

- **IDE**: PyCharm (IntelliJ-based Python IDE)
- **Language**: Python
- **Target**: Command-line interface tool

## Project Structure

```
.
├── src/
│   └── claude_extend/
│       ├── __init__.py     # Package initialization
│       └── main.py         # Main CLI entry point
├── pyproject.toml          # Project configuration and dependencies
├── README.md              # Project documentation
├── CLAUDE.md              # This file
├── .idea/                 # PyCharm IDE configuration files
└── .gitignore             # Git ignore rules for Python/JetBrains
```

## Architecture

This tool manages MCP server connections for Claude Code by:
- Linking already-installed MCP servers to Claude Code configuration
- Unlinking MCP servers from Claude Code configuration
- Listing currently connected MCP servers
- Managing Claude Code's MCP configuration file updates
- Assumes MCP servers are already installed on the system

## Development Commands

**Run during development:**
```bash
python -m src.claude_extend.main
```

**Test the package locally:**
```bash
uv run python -m src.claude_extend.main
```

**Install for testing:**
```bash
uv tool install .
cx
```

## Installation Methods

**Run without installation (recommended for users):**
```bash
uvx --from git+https://github.com/cearley/claude-extend cx
```

**Install locally from GitHub:**
```bash
uv tool install git+https://github.com/cearley/claude-extend
```

**Install from source:**
```bash
git clone https://github.com/cearley/claude-extend.git
cd claude-extend
uv tool install .
```

## Testing

**Run all tests:**
```bash
uv run pytest
```

**Run tests with coverage:**
```bash
uv run pytest --cov=claude_extend --cov-report=term-missing
```

**Run specific test file:**
```bash
uv run pytest tests/test_tools.py -v
```

**Install development dependencies:**
```bash
uv sync --extra dev
```

## Test Structure

- `tests/test_tools.py` - Unit tests for MCP tool registry and management
- `tests/test_utils.py` - Unit tests for utility functions and validation
- `tests/test_cli.py` - Integration tests for CLI commands
- `tests/conftest.py` - Shared test fixtures and configuration

## MCP Integration Notes

- MCP servers extend Claude Code's capabilities through additional tools
- Configuration typically stored in Claude Code's settings/config files
- Tool should handle JSON configuration management
- May need to interact with Claude Code's MCP server registry