"""Tests for the utils module."""

import pytest
import sys
import os
from unittest.mock import patch, mock_open
from pathlib import Path
from io import StringIO

from claude_extend.utils import (
    Colors, print_message, validate_environment,
    validate_interactive_environment
)


class TestColors:
    """Test cases for Colors class."""

    def test_color_constants(self):
        """Test that color constants are defined."""
        assert hasattr(Colors, 'RED')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'YELLOW')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'NC')

        # Test they're strings starting with ANSI escape
        assert Colors.RED.startswith('\033[')
        assert Colors.GREEN.startswith('\033[')
        assert Colors.YELLOW.startswith('\033[')
        assert Colors.BLUE.startswith('\033[')
        assert Colors.NC == '\033[0m'


class TestPrintMessage:
    """Test cases for print_message function."""

    def test_print_message_info(self, capsys):
        """Test printing info messages."""
        print_message('info', 'Test message')
        captured = capsys.readouterr()

        assert 'Test message' in captured.err
        assert 'ℹ️' in captured.err
        assert Colors.BLUE in captured.err
        assert Colors.NC in captured.err

    def test_print_message_success(self, capsys):
        """Test printing success messages."""
        print_message('success', 'Success message')
        captured = capsys.readouterr()

        assert 'Success message' in captured.err
        assert '✅' in captured.err
        assert Colors.GREEN in captured.err

    def test_print_message_warning(self, capsys):
        """Test printing warning messages."""
        print_message('warning', 'Warning message')
        captured = capsys.readouterr()

        assert 'Warning message' in captured.err
        assert '⚠️' in captured.err
        assert Colors.YELLOW in captured.err

    def test_print_message_error(self, capsys):
        """Test printing error messages."""
        print_message('error', 'Error message')
        captured = capsys.readouterr()

        assert 'Error message' in captured.err
        assert '❌' in captured.err
        assert Colors.RED in captured.err

    def test_print_message_unknown_level(self, capsys):
        """Test printing with unknown level defaults to info."""
        print_message('unknown', 'Unknown level')
        captured = capsys.readouterr()

        assert 'Unknown level' in captured.err
        assert 'ℹ️' in captured.err
        assert Colors.BLUE in captured.err


class TestValidateEnvironment:
    """Test cases for validate_environment function."""

    @patch('pathlib.Path.exists')
    @patch('shutil.which')
    def test_validate_environment_success(self, mock_which, mock_exists, capsys):
        """Test successful environment validation."""
        # Mock project file exists and claude CLI available
        mock_exists.side_effect = lambda: mock_exists.call_count == 1  # First call returns True
        mock_which.return_value = '/usr/bin/claude'

        result = validate_environment()

        assert result is True
        captured = capsys.readouterr()
        assert '✅' in captured.err
        assert 'Project directory detected' in captured.err

    @patch('pathlib.Path.exists')
    def test_validate_environment_no_project_files(self, mock_exists, capsys):
        """Test validation failure when no project files found."""
        mock_exists.return_value = False

        result = validate_environment()

        assert result is False
        captured = capsys.readouterr()
        assert '❌' in captured.err
        assert 'project directory' in captured.err

    @patch('pathlib.Path.exists')
    @patch('shutil.which')
    def test_validate_environment_no_claude_cli(self, mock_which, mock_exists, capsys):
        """Test validation failure when Claude CLI not found."""
        mock_exists.side_effect = lambda: mock_exists.call_count == 1  # First call returns True
        mock_which.return_value = None

        result = validate_environment()

        assert result is False
        captured = capsys.readouterr()
        assert '❌' in captured.err
        assert 'Claude CLI not found' in captured.err


class TestValidateInteractiveEnvironment:
    """Test cases for validate_interactive_environment function."""

    @patch('claude_extend.utils.validate_environment')
    @patch('sys.stdin.isatty')
    def test_validate_interactive_success(self, mock_isatty, mock_validate_env):
        """Test successful interactive environment validation."""
        mock_validate_env.return_value = True
        mock_isatty.return_value = True

        result = validate_interactive_environment()

        assert result is True

    @patch('claude_extend.utils.validate_environment')
    def test_validate_interactive_environment_fail(self, mock_validate_env):
        """Test failure when base environment validation fails."""
        mock_validate_env.return_value = False

        result = validate_interactive_environment()

        assert result is False

    @patch('claude_extend.utils.validate_environment')
    @patch('sys.stdin.isatty')
    def test_validate_interactive_not_tty(self, mock_isatty, mock_validate_env, capsys):
        """Test failure when not in interactive terminal."""
        mock_validate_env.return_value = True
        mock_isatty.return_value = False

        result = validate_interactive_environment()

        assert result is False
        captured = capsys.readouterr()
        assert 'interactive input' in captured.err