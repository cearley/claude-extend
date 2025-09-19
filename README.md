# Claude eXtend (cx)

[![CI](https://github.com/cearley/claude-extend/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/cearley/claude-extend/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)](https://github.com/cearley/claude-extend/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/release/cearley/claude-extend.svg)](https://github.com/cearley/claude-extend/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub last commit](https://img.shields.io/github/last-commit/cearley/claude-extend)](https://github.com/cearley/claude-extend/commits/main)

A CLI tool for managing Model Context Protocol (MCP) server connections with Claude Code.

Claude eXtend allows you to easily add, remove, and manage MCP servers that extend Claude Code's capabilities. It comes with opinionated default MCP tool definitions and can dynamically install servers (e.g., via npx or uvx) or work with pre-installed servers. The default tool definitions can be overridden or extended via external configuration files.

## Quick Start

Run `cx` instantly with `uvx` directly from GitHub (no installation required):

```bash
# List available MCP tools
uvx --from git+https://github.com/cearley/claude-extend cx list

# Add basic-memory MCP server to Claude Code
uvx --from git+https://github.com/cearley/claude-extend cx add basic-memory

# Interactive mode for guided tool selection
uvx --from git+https://github.com/cearley/claude-extend cx add --interactive
```

Or install locally from GitHub:

```bash
uv tool install git+https://github.com/cearley/claude-extend
cx list
cx add basic-memory
```

Or install from source:

```bash
git clone https://github.com/cearley/claude-extend.git
cd claude-extend
uv tool install .
cx add --interactive
```

## Table of Contents

- [Why use cx instead of `claude mcp` directly?](#why-use-cx-instead-of-claude-mcp-directly)
- [Usage](#usage)
  - [Interactive Mode](#interactive-mode)
- [External Configuration](#external-configuration)
  - [Configuration File Locations](#configuration-file-locations)
  - [Configuration File Format](#configuration-file-format)
  - [Example: Adding basic-memory](#example-adding-basic-memory)
- [What are MCP Servers?](#what-are-mcp-servers)
- [Security Considerations](#security-considerations)
- [Requirements](#requirements)
- [Development](#development)
- [License](#license)

## Why use cx instead of `claude mcp` directly?

The main benefit of `cx` is **organization**: your selected MCP tools are codified in a configuration file, making them easy to add, remove, and share:

- **📝 Codified setup**: Your MCP tools are defined in a JSON config with exact installation commands
- **🔄 Reproducible**: Share your `tools.json` with teammates or across machines
- **🎯 Curated collection**: Maintain a focused set of tools relevant to your workflow
- **⚡ Quick access**: Add/remove tools by name without remembering complex installation syntax

While `claude mcp add` works fine for one-off installations, `cx` helps when you want to maintain and organize a consistent set of MCP tools over time.

## Usage

```bash
cx                    # Show help and available commands
cx list              # List available MCP tools
cx add <tool>        # Add an MCP tool to Claude Code
cx add --interactive # Interactive tool selection menu
cx remove <tool>     # Remove an MCP tool from Claude Code
```

### Interactive Mode

For a guided experience, use interactive mode to select and install multiple tools:

```bash
cx add --interactive
```

Interactive mode provides:
- 📋 List of all available tools with installation status
- 🎯 Multi-select tool installation
- ✅ Prerequisites checking before installation
- 📦 Batch installation of selected tools

## External Configuration

Claude eXtend can load custom MCP tool definitions from an external configuration file. This allows you to add your own MCP servers without modifying the source code.

### Configuration File Locations

Claude eXtend checks for configuration files in this order:

1. **Environment variable**: `CLAUDE_EXTEND_CONFIG` (full path to config file)
2. **User config directory**: `~/.config/claude-extend/tools.json`
3. **Home directory**: `~/.claude-extend/tools.json`

### Configuration File Format

Create a JSON file with the following structure:

```json
{
  "tools": {
    "my-custom-server": {
      "name": "my-custom-server",
      "description": "My custom MCP server",
      "prerequisite": "npx",
      "error_message": "npx not found. Please install Node.js first.",
      "install_command": ["claude", "mcp", "add", "my-custom-server", "--", "npx", "-y", "my-custom-server"]
    }
  }
}
```

### Example: Adding basic-memory

This example shows how to add [basic-memory](https://github.com/basicmachines-co/basic-memory), an AI-powered memory system, to your Claude eXtend configuration.

**Step 1: Install basic-memory**

First, install basic-memory on your system ([installation guide](https://docs.basicmemory.com/getting-started/#installation)):

```bash
curl -LsSf https://basicmemory.com/install/latest.sh | sh
```

**Step 2: Create external configuration**

Create a configuration file to tell Claude eXtend about basic-memory:

```bash
# Create config directory
mkdir -p ~/.config/claude-extend

# Create your tools.json file
cat > ~/.config/claude-extend/tools.json << 'EOF'
{
  "tools": {
    "basic-memory": {
      "name": "basic-memory",
      "description": "AI-powered memory system for contextual understanding",
      "prerequisite": "basic-memory",
      "error_message": "basic-memory not found. Install with: curl -LsSf https://basicmemory.com/install/latest.sh | sh",
      "install_command": ["claude", "mcp", "add", "basic-memory", "basic-memory", "mcp"]
    }
  }
}
EOF
```

**Step 3: Use with Claude eXtend**

Now basic-memory will appear in your available tools:

```bash
# List available tools (basic-memory should now appear)
cx list

# Add basic-memory to Claude Code
cx add basic-memory
```

**How it works:**

- The `"prerequisite": "basic-memory"` field tells Claude eXtend to check if the `basic-memory` command is available in your system PATH before attempting to add it
- After running the installation script, `basic-memory` becomes a valid system command that can be executed from anywhere
- Claude eXtend uses Python's `shutil.which()` to verify the prerequisite exists before proceeding
- The `install_command` uses the Claude Code MCP configuration command documented in the [basic-memory Claude Code integration guide](https://docs.basicmemory.com/integrations/claude-code/#configure-claude-code)

When you run `cx add basic-memory`, Claude eXtend will first check that the `basic-memory` command is available, then execute the install command to configure Claude Code with the basic-memory MCP server.

## What are MCP Servers?

Model Context Protocol (MCP) servers extend Claude Code's capabilities by providing additional tools and context. Examples include:

- File system access tools
- Database connection tools
- API integration tools
- Development environment tools

Claude eXtend helps you manage which of these installed servers are active in your Claude Code setup.

## Security Considerations

⚠️ **Important**: The `install_command` entries in external `tools.json` configuration files are executed directly on your machine. Only use configuration files from trusted sources, and always review their contents before use. Treat these files like any other script - they should be reviewed and trusted before execution.

## Requirements

- Python 3.8+
- `uv` package manager (for `uvx` usage)

## Development

See [CLAUDE.md](CLAUDE.md) for development guidance.

## Development Notes

This project utilized AI assistance, specifically Claude, for certain aspects of its development, including:

- Generating initial code structures and CLI architecture
- Implementing comprehensive test suites with proper mocking strategies
- Drafting and refining documentation sections
- Assisting with debugging, performance optimization, and problem-solving
- Code review and best practices recommendations

## License

MIT