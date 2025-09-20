"""Unit tests for CLI command functions."""

from unittest.mock import patch, MagicMock

import pytest
from claude_extend.main import (
    cmd_list, cmd_add, cmd_remove, cmd_remove_interactive,
    _get_user_tool_removal_selection, _remove_selected_tools
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
        args.interactive = False

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

    @patch('claude_extend.main.validate_interactive_environment')
    @patch('claude_extend.main._install_selected_tools')
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
        mock_install_tools.assert_called_once_with(['prereq-missing-tool'], {'prereq-missing-tool': mock_tool},
                                                   mock_registry)

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
    def test_cmd_remove_interactive_no_tools_available(self, mock_validate, capsys):
        """Test interactive remove with no tools in registry."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {}
        args = MagicMock()

        cmd_remove_interactive(args, mock_registry)
        captured = capsys.readouterr()

        assert 'No tools available in registry.' in captured.err

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
    @patch('claude_extend.main._remove_selected_tools')
    @patch('questionary.checkbox')
    def test_cmd_remove_interactive_with_selection(self, mock_checkbox, mock_remove_tools, mock_validate):
        """Test interactive remove command with tool selection."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = True
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}
        mock_checkbox.return_value.ask.return_value = ['test-tool']
        args = MagicMock()

        cmd_remove_interactive(args, mock_registry)

        mock_checkbox.assert_called_once()
        mock_remove_tools.assert_called_once_with(['test-tool'], {'test-tool': mock_tool}, mock_registry)

    @patch('questionary.checkbox')
    def test_get_user_tool_removal_selection_non_installed_filtered(self, mock_checkbox, capsys):
        """Test _get_user_tool_removal_selection filters out non-installed tools."""
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = False
        tools = {'test-tool': mock_tool}
        mock_checkbox.return_value.ask.return_value = ['test-tool']  # User selected non-installed tool

        result = _get_user_tool_removal_selection(tools, mock_registry)
        captured = capsys.readouterr()

        assert result == []
        assert 'test-tool is not installed, skipping.' in captured.err

    @patch('questionary.checkbox')
    def test_get_user_tool_removal_selection_user_cancel(self, mock_checkbox):
        """Test _get_user_tool_removal_selection when user cancels."""
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = True
        tools = {'test-tool': mock_tool}
        mock_checkbox.return_value.ask.return_value = None  # User cancelled

        result = _get_user_tool_removal_selection(tools, mock_registry)

        assert result == []

    @patch('questionary.checkbox')
    def test_get_user_tool_removal_selection_with_selection(self, mock_checkbox):
        """Test _get_user_tool_removal_selection with tool selection."""
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.is_installed.return_value = True
        tools = {'test-tool': mock_tool}
        mock_checkbox.return_value.ask.return_value = ['test-tool']

        result = _get_user_tool_removal_selection(tools, mock_registry)

        assert result == ['test-tool']

    @patch('questionary.checkbox')
    def test_get_user_tool_removal_selection_shows_status_indicators(self, mock_checkbox):
        """Test _get_user_tool_removal_selection shows status indicators for tools."""
        mock_registry = MagicMock()

        # Create mock tools with different statuses
        mock_installed_tool = MagicMock()
        mock_installed_tool.is_installed.return_value = True
        mock_installed_tool.check_prerequisites.return_value = True
        mock_installed_tool.description = "Installed tool"

        mock_not_installed_tool = MagicMock()
        mock_not_installed_tool.is_installed.return_value = False
        mock_not_installed_tool.description = "Not installed tool"

        tools = {
            'installed-tool': mock_installed_tool,
            'not-installed-tool': mock_not_installed_tool
        }
        mock_checkbox.return_value.ask.return_value = []  # User selects nothing

        _get_user_tool_removal_selection(tools, mock_registry)

        # Verify questionary was called with correct status indicators
        mock_checkbox.assert_called_once()
        call_args = mock_checkbox.call_args
        choices = call_args[1]['choices']

        # Find the choices by their values
        installed_choice = next(c for c in choices if c.value == 'installed-tool')
        not_installed_choice = next(c for c in choices if c.value == 'not-installed-tool')

        assert "(not installed)" not in installed_choice.title
        assert "(not installed)" in not_installed_choice.title

    def test_remove_selected_tools_success(self, capsys):
        """Test _remove_selected_tools with successful removal."""
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.description = "Test tool"
        mock_tool.remove.return_value = True
        tools = {'test-tool': mock_tool}

        _remove_selected_tools(['test-tool'], tools, mock_registry)

        captured = capsys.readouterr()
        assert 'Removing 1 MCP tool(s)...' in captured.err
        assert 'Processing: Test tool' in captured.err
        assert '✓ test-tool removed successfully' in captured.err
        assert 'MCP tool removal complete!' in captured.err

    def test_remove_selected_tools_failure(self, capsys):
        """Test _remove_selected_tools with failed removal."""
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.description = "Test tool"
        mock_tool.remove.return_value = False
        tools = {'test-tool': mock_tool}

        _remove_selected_tools(['test-tool'], tools, mock_registry)

        captured = capsys.readouterr()
        assert 'Removing 1 MCP tool(s)...' in captured.err
        assert 'Processing: Test tool' in captured.err
        assert '✗ Failed to remove test-tool' in captured.err
        assert 'MCP tool removal complete!' in captured.err


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
        mock_registry.get_tool_names.return_value = ['test-tool', 'other-tool']

        cmd_func(args, mock_registry)
        captured = capsys.readouterr()

        assert 'Unknown tool: unknown-tool' in captured.err
        assert 'Available tools: test-tool, other-tool' in captured.err
