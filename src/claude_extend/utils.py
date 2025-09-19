"""Utility functions for Claude eXtend."""

import os
import sys
import shutil
from pathlib import Path


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
        print_message('error', "This command must be run from within a project directory")
        print_message('info', "Look for files like package.json, pyproject.toml, Cargo.toml, .git, or go.mod")
        return False

    if not shutil.which('claude'):
        print_message('error', "Claude CLI not found. Please install it first.")
        return False

    print_message('success', f"Project directory detected: {os.getcwd()}")
    return True


def validate_interactive_environment() -> bool:
    """Validate environment for interactive commands."""
    if not validate_environment():
        return False

    if not sys.stdin.isatty():
        print_message('error', "This command requires interactive input.")
        return False

    return True