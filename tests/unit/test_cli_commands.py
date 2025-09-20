"""Unit tests for CLI command functions."""

import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO

from claude_extend.main import cmd_list, cmd_add, cmd_remove


class TestListCommand:
    """Test the list command."""

    def test_cmd_list_with_tools(self, mock_registry, capsys):
        """Test list command with available tools."""
        args = MagicMock()

        cmd_list(args, mock_registry)
        captured = capsys.readouterr()

        assert '🔧 Available MCP Tools' in captured.out
        assert 'Test Tool - A tool for testing' in captured.out
        assert 'Another Tool - Another testing tool' in captured.out
        assert 'Total: 2 tools' in captured.out


class TestAddCommand:
    """Test the add command."""

    @patch('claude_extend.main.validate_environment')
    def test_cmd_add_no_tools_specified(self, mock_validate, mock_registry, capsys):
        """Test add command with no tools specified."""
        args = MagicMock()
        args.interactive = False
        args.tools = []

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools specified' in captured.err
        mock_validate.assert_not_called()

    @patch('claude_extend.main.validate_environment')
    def test_cmd_add_unknown_tool(self, mock_validate, mock_registry, capsys):
        """Test add command with unknown tool."""
        mock_validate.return_value = True
        args = MagicMock()
        args.interactive = False
        args.tools = ['unknown-tool']

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Unknown tool: unknown-tool' in captured.err

    @patch('claude_extend.main.validate_environment')
    def test_cmd_add_valid_tool_success(self, mock_validate, capsys):
        """Test successful tool installation."""
        mock_validate.return_value = True
        args = MagicMock()
        args.interactive = False
        args.tools = ['test-tool']

        # Mock tool installation success
        mock_tool = MagicMock()
        mock_tool.check_prerequisites.return_value = True
        mock_tool.install.return_value = True
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = mock_tool

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Processing: Test Tool' in captured.err
        assert '✓ test-tool installed successfully' in captured.err
        mock_tool.install.assert_called_once()

    @patch('claude_extend.main.validate_environment')
    def test_cmd_add_prerequisites_missing(self, mock_validate, capsys):
        """Test tool installation with missing prerequisites."""
        mock_validate.return_value = True
        args = MagicMock()
        args.interactive = False
        args.tools = ['test-tool']

        # Mock missing prerequisites
        mock_tool = MagicMock()
        mock_tool.check_prerequisites.return_value = False
        mock_tool.error_message = "Python not found"
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = mock_tool

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Prerequisites not met' in captured.err
        assert 'Python not found' in captured.err
        mock_tool.install.assert_not_called()


class TestRemoveCommand:
    """Test cmd_remove function."""

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_no_tools_specified(self, mock_validate, capsys):
        """Test remove command with no tools specified."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = []

        mock_registry = MagicMock()

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools specified. Specify tool names to remove.' in captured.err

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_unknown_tool(self, mock_validate, capsys):
        """Test remove command with unknown tool."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = ['unknown-tool']

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = None
        mock_registry.get_tool_names.return_value = ['test-tool', 'other-tool']

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Unknown tool: unknown-tool' in captured.err
        assert 'Available tools: test-tool, other-tool' in captured.err

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_valid_tool_success(self, mock_validate, capsys):
        """Test successful tool removal."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = ['test-tool']

        # Mock tool removal success
        mock_tool = MagicMock()
        mock_tool.remove.return_value = True
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = mock_tool

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Processing: Test Tool' in captured.err
        assert '✓ test-tool removed successfully' in captured.err
        mock_tool.remove.assert_called_once()

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_tool_failure(self, mock_validate, capsys):
        """Test failed tool removal."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = ['test-tool']

        # Mock tool removal failure
        mock_tool = MagicMock()
        mock_tool.remove.return_value = False
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = mock_tool

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Processing: Test Tool' in captured.err
        assert '✗ Failed to remove test-tool' in captured.err
        mock_tool.remove.assert_called_once()


class TestAddInteractiveCommand:
    """Test the interactive add command."""

    @patch('claude_extend.main.validate_interactive_environment')
    def test_cmd_add_interactive_environment_fail(self, mock_validate, mock_registry):
        """Test interactive command when environment validation fails."""
        mock_validate.return_value = False
        args = MagicMock()
        args.interactive = True

        with pytest.raises(SystemExit):
            cmd_add(args, mock_registry)

    @patch('claude_extend.main.validate_interactive_environment')
    def test_cmd_add_interactive_all_installed(self, mock_validate, capsys):
        """Test interactive command when all tools are already installed."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.get_available_tools.return_value = []
        args = MagicMock()
        args.interactive = True

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'All tools are already installed!' in captured.err

    @patch('claude_extend.main.validate_interactive_environment')
    @patch('questionary.checkbox')
    def test_cmd_add_interactive_quit(self, mock_checkbox, mock_validate):
        """Test interactive command with quit selection."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.get_available_tools.return_value = ['test-tool']
        mock_registry.list_tools.return_value = {'test-tool': MagicMock()}
        mock_checkbox.return_value.ask.return_value = None  # User cancelled/quit
        args = MagicMock()
        args.interactive = True

        cmd_add(args, mock_registry)
        mock_checkbox.assert_called_once()