# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Claude eXtend (cx)** - A Python command-line tool for managing Model Context Protocol (MCP) servers that extend Claude Code's capabilities. The tool provides organized access to MCP tools through configuration files, with commands to add, remove, and list MCP servers. It can dynamically install servers (e.g., via npx or uvx) or work with pre-installed servers.

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
│       ├── main.py         # Main CLI entry point and commands
│       ├── tools.py        # MCP tool registry and management
│       └── utils.py        # Utility functions and validation
├── tests/                  # Test suite
│   ├── test_cli.py        # CLI command integration tests
│   ├── test_tools.py      # Tool registry and management tests
│   ├── test_utils.py      # Utility function tests
│   └── conftest.py        # Test fixtures and configuration
├── pyproject.toml          # Project configuration and dependencies
├── README.md              # Project documentation
├── CLAUDE.md              # This file
├── .idea/                 # PyCharm IDE configuration files
└── .gitignore             # Git ignore rules for Python/JetBrains
```

## Architecture

This tool manages MCP server connections for Claude Code by:
- Adding MCP servers to Claude Code configuration (via `claude mcp add`)
- Removing MCP servers from Claude Code configuration (via `claude mcp remove`)
- Listing available and installed MCP tools with status
- Managing external configuration files for custom tool definitions
- Supporting both dynamic installation (npx/uvx) and pre-installed servers
- Providing interactive mode for guided tool selection
- Caching `claude mcp list` output for performance

### Core Components

- **MCPTool**: Represents individual tools with prerequisites, descriptions, and install commands
- **MCPToolRegistry**: Manages the collection of available tools and handles external config loading
- **CLI Commands**: `list`, `add`, `add --interactive`, `remove`
- **External Config**: JSON-based tool definitions for extensibility

## Development Commands

**Install dependencies:**
```bash
uv sync
```

**Install development dependencies:**
```bash
uv sync --extra dev
```

**Run during development:**
```bash
python -m src.claude_extend.main
```

**Test the package locally:**
```bash
uv run cx
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

**Run only unit tests:**
```bash
uv run pytest tests/unit/
```

**Run only integration tests:**
```bash
uv run pytest tests/integration/
```

**Run tests with coverage:**
```bash
uv run pytest --cov=claude_extend --cov-report=term-missing
```

## Test Structure

Tests are organized into unit and integration categories:

**Unit tests** (`tests/unit/`):
- `test_tools.py` - Unit tests for MCP tool registry and management classes
- `test_utils.py` - Unit tests for utility functions and validation
- `test_cli_commands.py` - Unit tests for individual CLI command functions

**Integration tests** (`tests/integration/`):
- `test_cli_integration.py` - End-to-end tests through the main() entry point

**Shared test configuration:**
- `tests/conftest.py` - Shared test fixtures including `claude mcp` subprocess mocking

### Test Mocking

Unit tests mock all external dependencies including:
- `subprocess.run` calls to `claude mcp` commands (via `mock_claude_mcp_calls` fixture)
- `shutil.which` for prerequisite checking (via `mock_shutil_which` fixture)
- File system operations for external configuration testing

This ensures unit tests can run in CI environments without requiring Claude CLI to be installed.

### Test Coverage

The test suite covers:
- **MCPTool class**: Installation, removal, prerequisite checking, with registry caching
- **MCPToolRegistry class**: Tool discovery, external config loading, installation status caching
- **CLI commands**: All commands including interactive mode, error handling, argument parsing
- **External configuration**: Loading, validation, fallback to defaults
- **Caching optimization**: Ensures `claude mcp list` is called only once per command execution

## MCP Integration Notes

- MCP servers extend Claude Code's capabilities through additional tools
- Configuration typically stored in Claude Code's settings/config files
- Tool should handle JSON configuration management
- May need to interact with Claude Code's MCP server registry

## External Configuration

Claude eXtend supports loading custom MCP tool definitions from external JSON configuration files. This allows extending the tool registry without modifying source code.

### Configuration File Locations (checked in order)

1. **Environment variable**: `CLAUDE_EXTEND_CONFIG` (full path to config file)
2. **User config directory**: `~/.config/claude-extend/tools.json`
3. **Home directory**: `~/.claude-extend/tools.json`

### Configuration Format

```json
{
  "tools": {
    "tool-name": {
      "name": "tool-name",
      "description": "Tool description",
      "prerequisite": "command-executable",
      "error_message": "Error when prerequisite missing",
      "install_command": ["array", "of", "command", "args"]
    }
  }
}
```

### Key Implementation Details

- **prerequisite**: Name of executable checked with `shutil.which()`. Special case: "npm" checks for either `npm` or `npx`
- **install_command**: Array of command arguments. Supports `{project_dir}` placeholder replacement
- External config loading is handled in `MCPToolRegistry._load_tools()` with fallback to hardcoded defaults
- Configuration validation and loading functions in `utils.py`: `get_config_path()`, `load_external_tools_config()`