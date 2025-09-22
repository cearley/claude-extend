"""Unit tests for CLI command functions."""

from unittest.mock import patch, MagicMock

import pytest
from claude_extend.main import (
    cmd_list, cmd_add, cmd_remove, cmd_remove_interactive,
    _get_user_tool_selection, _process_tools
)


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
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}

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
        mock_tool.command = "python"
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}

        cmd_add(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Prerequisites not met' in captured.err
        assert 'python not found' in captured.err
        mock_tool.install.assert_not_called()


class TestRemoveCommand:
    """Test cmd_remove function."""

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_no_tools_specified(self, mock_validate, capsys):
        """Test remove command with no tools specified."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = []
        args.interactive = False

        mock_registry = MagicMock()

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools specified. Use --interactive or specify tool names to remove.' in captured.err

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_valid_tool_success(self, mock_validate, capsys):
        """Test successful tool removal."""
        mock_validate.return_value = True
        args = MagicMock()
        args.tools = ['test-tool']
        args.interactive = False

        # Mock tool removal success
        mock_tool = MagicMock()
        mock_tool.remove.return_value = True
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}

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
        args.interactive = False

        # Mock tool removal failure
        mock_tool = MagicMock()
        mock_tool.remove.return_value = False
        mock_tool.description = "Test Tool"

        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}

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

    @patch('claude_extend.main.validate_interactive_environment')
    @patch('claude_extend.main._process_tools')
    @patch('questionary.checkbox')
    def test_cmd_add_interactive_with_prerequisites_missing(self, mock_checkbox, mock_install_tools, mock_validate):
        """Test interactive add command with tool selection that has missing prerequisites."""
        mock_validate.return_value = True
        mock_registry = MagicMock()

        # Create a tool with missing prerequisites
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = False
        mock_tool.check_prerequisites.return_value = False
        mock_tool.description = "Tool with missing prereqs"

        mock_registry.get_available_tools.return_value = ['prereq-missing-tool']
        mock_registry.list_tools.return_value = {'prereq-missing-tool': mock_tool}
        mock_checkbox.return_value.ask.return_value = ['prereq-missing-tool']
        args = MagicMock()
        args.interactive = True

        cmd_add(args, mock_registry)

        # Verify the tool was selected and passed to install function
        mock_checkbox.assert_called_once()
        # Verify _process_tools was called with the correct parameters
        mock_install_tools.assert_called_once()

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_interactive_flag(self, mock_validate):
        """Test that remove command routes to interactive when --interactive flag is used."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        args = MagicMock()
        args.interactive = True
        args.tools = []

        with patch('claude_extend.main.cmd_remove_interactive') as mock_interactive:
            cmd_remove(args, mock_registry)
            mock_interactive.assert_called_once_with(args, mock_registry)

    @patch('claude_extend.main.validate_environment')
    def test_cmd_remove_no_interactive_no_tools(self, mock_validate, capsys):
        """Test remove command with no tools and no interactive flag."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        args = MagicMock()
        args.interactive = False
        args.tools = []

        cmd_remove(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools specified. Use --interactive or specify tool names to remove.' in captured.err

    @patch('claude_extend.main.validate_interactive_environment')
    def test_cmd_remove_interactive_no_tools_installed(self, mock_validate, capsys):
        """Test interactive remove with no tools installed."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {'test-tool': MagicMock()}
        mock_registry.get_installed_tools.return_value = []
        args = MagicMock()

        cmd_remove_interactive(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools are currently installed.' in captured.err

    @patch('claude_extend.main.validate_interactive_environment')
    @patch('questionary.checkbox')
    def test_cmd_remove_interactive_quit(self, mock_checkbox, mock_validate):
        """Test interactive remove command with quit selection."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {'test-tool': MagicMock()}
        mock_checkbox.return_value.ask.return_value = None  # User cancelled/quit
        args = MagicMock()

        cmd_remove_interactive(args, mock_registry)
        mock_checkbox.assert_called_once()

    @patch('claude_extend.main.validate_interactive_environment')
    @patch('claude_extend.main._process_tools')
    @patch('questionary.checkbox')
    def test_cmd_remove_interactive_with_selection(self, mock_checkbox, mock_process_tools, mock_validate):
        """Test interactive remove command with tool selection."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = True
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}
        mock_registry.get_installed_tools.return_value = ['test-tool']
        mock_checkbox.return_value.ask.return_value = ['test-tool']
        args = MagicMock()

        cmd_remove_interactive(args, mock_registry)

        mock_checkbox.assert_called_once()
        mock_process_tools.assert_called_once()

    # Tests for removed functions have been removed since the functions were consolidated


class TestCommandUnknownTools:
    """Parameterized tests for unknown tool handling across commands."""

    @pytest.mark.parametrize("cmd_func,command_name", [
        (cmd_add, "add"),
        (cmd_remove, "remove"),
    ])
    @patch('claude_extend.main.validate_environment')
    def test_unknown_tool_handling(self, mock_validate, cmd_func, command_name, capsys):
        """Test unknown tool handling for both add and remove commands."""
        mock_validate.return_value = True
        args = MagicMock()
        args.interactive = False
        args.tools = ['unknown-tool']

        mock_registry = MagicMock()
        mock_registry.get_tool.return_value = None
        mock_registry.list_tools.return_value = {'test-tool': MagicMock(), 'other-tool': MagicMock()}

        cmd_func(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Unknown tool: unknown-tool' in captured.err
        assert 'Available tools: test-tool, other-tool' in captured.err
