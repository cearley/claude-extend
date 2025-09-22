"""Utility functions for Claude eXtend."""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def print_message(level: str, message: str) -> None:
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
    if not validate_environment():
        return False

    if not sys.stdin.isatty():
        print_message('error', "This command requires interactive input.")
        return False

    return True


def get_config_path() -> Optional[Path]:
    
    env_config = os.environ.get('CLAUDE_EXTEND_CONFIG')
    if env_config:
        config_path = Path(env_config)
        if config_path.exists():
            return config_path
    
    config_locations = [
        Path.home() / '.config' / 'claude-extend' / 'tools.json',
        Path.home() / '.claude-extend' / 'tools.json'
    ]
    
    for config_path in config_locations:
        if config_path.exists():
            return config_path
    
    return None


def load_external_tools_config(config_path: Path) -> Dict[str, Dict[str, any]]:
    import json
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    return config_data.get('tools', {})
