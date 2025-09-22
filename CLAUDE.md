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
│   ├── unit/              # Unit tests
│   │   ├── test_cli_commands.py  # CLI command unit tests
│   │   ├── test_tools.py         # Tool registry unit tests
│   │   └── test_utils.py         # Utility function unit tests
│   ├── integration/       # Integration tests
│   │   └── test_cli_integration.py  # End-to-end CLI tests
│   └── conftest.py        # Test fixtures and configuration
├── .github/               # GitHub workflows and configuration
│   └── workflows/
│       └── ci.yml         # CI/CD pipeline
├── pyproject.toml         # Project configuration and dependencies
├── tools.json.example     # Example external configuration file
├── README.md              # Project documentation
├── CLAUDE.md              # This file
└── .gitignore             # Git ignore rules
```

## Architecture

This tool manages MCP server connections for Claude Code by:
- Adding MCP servers to Claude Code configuration (via `claude mcp add`)
- Removing MCP servers from Claude Code configuration (via `claude mcp remove`)
- Listing available and installed MCP tools with status
- Managing external configuration files for custom tool definitions
- Supporting both dynamic installation (npx/uvx) and pre-installed servers
- Providing interactive mode for guided tool selection and removal
- Caching `claude mcp list` output for performance

### Core Components

- **MCPTool**: Represents individual tools with prerequisites, descriptions, and install commands
- **MCPToolRegistry**: Manages the collection of available tools and handles external config loading
- **CLI Commands**: `list`, `add`, `add --interactive`, `remove`, `remove --interactive`
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
uvx --from git+https://github.com/cearley/claude-extend@latest cx
```

**Install locally from GitHub:**
```bash
uv tool install git+https://github.com/cearley/claude-extend@latest
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

Claude eXtend uses the Claude Desktop MCP configuration format:

```json
{
  "tools": {
    "tool-name": {
      "description": "Tool description",
      "command": "command-executable",
      "args": ["array", "of", "command", "args"]
    }
  }
}
```

**Example Configuration:**

```json
{
  "tools": {
    "serena": {
      "description": "Semantic code analysis and intelligent IDE assistant",
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server",
        "--context", "ide-assistant", "--project", "{project_dir}"
      ]
    },
    "basic-memory": {
      "description": "Enhanced memory capabilities for Claude",
      "command": "basic-memory",
      "args": ["mcp"]
    },
    "filesystem": {
      "description": "File system access for Claude",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    }
  }
}
```

### Key Implementation Details

- **Claude Desktop Compatible**: Uses `command` and `args` fields directly, matching Claude Desktop's MCP configuration
- **Tool Name**: Tool name is derived from the JSON key, no redundant `name` field needed
- **Prerequisite Checking**: Automatically checks if the `command` is available using `shutil.which()` before installation
- **args**: Supports `{project_dir}` placeholder replacement for project-relative paths
- **Claude Desktop Export**: `MCPTool.to_claude_desktop_format()` method exports in Claude Desktop format
- **External Config Loading**: Handled in `MCPToolRegistry._load_tools()` with fallback to hardcoded defaults
- **Configuration Functions**: `get_config_path()`, `load_external_tools_config()` in `utils.py`

## Release Process

When creating a new release, follow these steps to maintain the `latest` tag:

### 1. Update Version
Update the version in `src/claude_extend/__init__.py`:
```python
__version__ = "x.y.z"
```

### 2. Run Tests
Ensure all tests pass:
```bash
uv run pytest
```

### 3. Create Version Tag and Latest Tag
```bash
# Create version-specific tag
git tag vx.y.z

# Move 'latest' tag to new release (delete old, create new)
git tag -d latest
git tag latest

# Or force update the latest tag in one command
git tag -f latest
```

### 4. Push to GitHub
```bash
# Push the commit
git push origin main

# Push the version tag
git push origin vx.y.z

# Force push the updated latest tag
git push -f origin latest
```

### 5. Create GitHub Release
Create a release on GitHub using the version tag (vx.y.z) for detailed release notes, while the `latest` tag provides an easy reference for users.

### Why Use a 'Latest' Tag?

The `latest` tag allows users to always install the most recent stable release without knowing the specific version number:

```bash
# Always gets the newest release
uvx --from git+https://github.com/cearley/claude-extend@latest cx list

# Instead of having to remember specific versions
uvx --from git+https://github.com/cearley/claude-extend@v0.2.0 cx list
```

### Git Tag Management Notes

- **Version tags** (v0.1.0, v0.2.0, etc.) are permanent and never moved
- **Latest tag** is a moving pointer that gets updated with each release
- Force pushing the `latest` tag is necessary and safe since it's designed to move
- Users who want stability should pin to specific version tags
- Users who want convenience should use the `latest` tag