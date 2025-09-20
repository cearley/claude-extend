"""Utility functions for Claude eXtend."""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_message(level: str, message: str) -> None:
    """Print colored messages to stderr."""
    icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    colors = {
        'info': Colors.BLUE,
        'success': Colors.GREEN,
        'warning': Colors.YELLOW,
        'error': Colors.RED
    }

    icon = icons.get(level, 'ℹ️')
    color = colors.get(level, Colors.BLUE)

    print(f"{color}{icon}  {message}{Colors.NC}", file=sys.stderr)


def validate_environment() -> bool:
    """Validate we're in a project directory and have Claude CLI."""
    project_files = ['package.json', 'pyproject.toml', 'Cargo.toml', '.git', 'go.mod']

    if not any(Path(f).exists() for f in project_files):
        print_message('warning', "No project directory detected")
        print_message('info', "Look for files like package.json, pyproject.toml, Cargo.toml, .git, or go.mod")
    else:
        print_message('success', f"Project directory detected: {os.getcwd()}")

    if not shutil.which('claude'):
        print_message('error', "Claude CLI not found. Please install it first.")
        return False

    return True


def validate_interactive_environment() -> bool:
    """Validate environment for interactive commands."""
    if not validate_environment():
        return False

    if not sys.stdin.isatty():
        print_message('error', "This command requires interactive input.")
        return False

    return True


def get_config_path() -> Optional[Path]:
    """Get the path to the external tools configuration file.

    Returns the first existing config file found, or None if no config exists.
    Checks in order:
    1. CLAUDE_EXTEND_CONFIG environment variable
    2. ~/.config/claude-extend/tools.json
    3. ~/.claude-extend/tools.json
    """
    
    # Check environment variable first
    env_config = os.environ.get('CLAUDE_EXTEND_CONFIG')
    if env_config:
        config_path = Path(env_config)
        if config_path.exists():
            return config_path
    
    # Check standard config locations
    config_locations = [
        Path.home() / '.config' / 'claude-extend' / 'tools.json',
        Path.home() / '.claude-extend' / 'tools.json'
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            return config_path
    
    return None


def load_external_tools_config(config_path: Path) -> Dict[str, Dict[str, any]]:
    """Load tools configuration from external JSON file.
    
    Expected JSON format:
    {
        "tools": {
            "tool-name": {
                "name": "tool-name",
                "description": "Tool description",
                "prerequisite": "command-name",
                "error_message": "Error message if prerequisite missing",
                "install_command": ["list", "of", "command", "args"]
            }
        }
    }
    
    Returns:
        Dict of tool configurations (not MCPTool objects to avoid circular imports)
    """
    import json
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return config_data.get('tools', {})
