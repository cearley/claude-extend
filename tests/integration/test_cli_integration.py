"""Integration tests for CLI commands."""

import pytest
import sys
from unittest.mock import patch, MagicMock

from claude_extend.main import main


class TestCLIArguments:
    """Test CLI argument parsing."""

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx'])
    def test_no_arguments_shows_help(self, mock_registry, capsys):
        """Test that running cx with no arguments shows help."""
        main()
        captured = capsys.readouterr()

        assert 'Claude eXtend (cx) - MCP Server Manager' in captured.out
        assert 'Version 0.2.0' in captured.out
        assert 'usage: cx' in captured.out

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', '--version'])
    def test_version_argument(self, mock_registry, capsys):
        """Test --version argument."""
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert 'cx 0.2.0' in captured.out

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', '--help'])
    def test_help_argument(self, mock_registry, capsys):
        """Test --help argument."""
        with pytest.raises(SystemExit):
            main()
        captured = capsys.readouterr()
        assert 'usage: cx' in captured.out
        assert 'List available MCP tools' in captured.out
        assert 'Add MCP tools' in captured.out


class TestListCommandIntegration:
    """Test list command integration."""

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', 'list'])
    def test_list_command_integration(self, mock_registry_class, capsys):
        """Test list command through main CLI."""
        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {
            "test-tool": MagicMock(description="Test Tool")
        }
        mock_registry.get_installed_tools.return_value = []
        mock_registry_class.return_value = mock_registry

        main()
        captured = capsys.readouterr()

        assert '🔧 Available MCP Tools' in captured.out
        mock_registry.list_tools.assert_called_once()
        mock_registry.get_installed_tools.assert_called_once()


class TestCLIIntegration:
    """Integration tests for the complete CLI."""

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', 'add', 'test-tool'])
    @patch('claude_extend.main.validate_environment')
    def test_add_command_integration(self, mock_validate, mock_registry_class, capsys):
        """Test add command through main CLI."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.description = "Test Tool"
        mock_tool.check_prerequisites.return_value = True
        mock_tool.install.return_value = True
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}
        mock_registry_class.return_value = mock_registry

        main()
        captured = capsys.readouterr()

        assert 'Processing: Test Tool' in captured.err
        mock_tool.install.assert_called_once()

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', 'add', '--interactive'])
    @patch('claude_extend.main.validate_interactive_environment')
    @patch('questionary.checkbox')
    def test_add_interactive_integration(self, mock_checkbox, mock_validate, mock_registry_class):
        """Test interactive add command through main CLI."""
        mock_validate.return_value = True
        mock_checkbox.return_value.ask.return_value = None  # User cancelled
        mock_registry = MagicMock()
        mock_registry.get_available_tools.return_value = ['test-tool']
        mock_registry.list_tools.return_value = {'test-tool': MagicMock()}
        mock_registry_class.return_value = mock_registry

        main()
        mock_checkbox.assert_called_once()

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', 'remove', 'test-tool'])
    @patch('claude_extend.main.validate_environment')
    def test_remove_command_integration(self, mock_validate, mock_registry_class, capsys):
        """Test remove command through main CLI."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_tool = MagicMock()
        mock_tool.description = "Test Tool"
        mock_tool.remove.return_value = True
        mock_registry.list_tools.return_value = {'test-tool': mock_tool}
        mock_registry_class.return_value = mock_registry

        main()
        captured = capsys.readouterr()

        assert 'Processing: Test Tool' in captured.err
        mock_tool.remove.assert_called_once()

    @patch('claude_extend.main.MCPToolRegistry')
    @patch('sys.argv', ['cx', 'remove', 'unknown-tool'])
    @patch('claude_extend.main.validate_environment')
    def test_remove_unknown_tool_integration(self, mock_validate, mock_registry_class, capsys):
        """Test remove command with unknown tool through main CLI."""
        mock_validate.return_value = True
        mock_registry = MagicMock()
        mock_registry.list_tools.return_value = {}
        mock_registry_class.return_value = mock_registry

        main()
        captured = capsys.readouterr()

        assert 'Unknown tool: unknown-tool' in captured.err