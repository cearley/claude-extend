"""Tests for the tools module."""

import json
import subprocess
from unittest.mock import patch, MagicMock

from claude_extend.tools import MCPTool, MCPToolRegistry


class TestMCPTool:
    """Test cases for MCPTool class."""

    def test_init(self, mock_tool):
        """Test MCPTool initialization."""
        assert mock_tool.name == "test-tool"
        assert mock_tool.description == "Test Tool - A tool for testing"
        assert mock_tool.prerequisite == "python"
        assert mock_tool.error_message == "Python not found"
        assert mock_tool.install_command == ["echo", "installing", "test-tool"]

    def test_check_prerequisites_available(self, mock_tool, mock_shutil_which):
        """Test prerequisite checking when available."""
        mock_shutil_which.return_value = "/usr/bin/python"
        assert mock_tool.check_prerequisites() is True

    def test_check_prerequisites_missing(self, mock_tool, mock_shutil_which):
        """Test prerequisite checking when missing."""
        mock_shutil_which.return_value = None
        assert mock_tool.check_prerequisites() is False

    def test_check_prerequisites_npm(self, mock_shutil_which):
        """Test npm prerequisite checking."""
        tool = MCPTool("test", "desc", "npm", "error", ["cmd"])

        # Test with npm available
        mock_shutil_which.side_effect = lambda cmd: "/usr/bin/npm" if cmd == "npm" else None
        assert tool.check_prerequisites() is True

        # Test with npx available
        mock_shutil_which.side_effect = lambda cmd: "/usr/bin/npx" if cmd == "npx" else None
        assert tool.check_prerequisites() is True

        # Test with neither available
        mock_shutil_which.side_effect = lambda cmd: None
        assert tool.check_prerequisites() is False

    def test_is_installed_true(self, mock_tool):
        """Test is_installed when tool is installed."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = True

        assert mock_tool.is_installed(mock_registry) is True
        mock_registry.is_tool_installed.assert_called_once_with("test-tool")

    def test_is_installed_false(self, mock_tool):
        """Test is_installed when tool is not installed."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False

        assert mock_tool.is_installed(mock_registry) is False
        mock_registry.is_tool_installed.assert_called_once_with("test-tool")

    def test_is_installed_subprocess_error(self, mock_tool):
        """Test is_installed when subprocess error occurs."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False

        assert mock_tool.is_installed(mock_registry) is False
        mock_registry.is_tool_installed.assert_called_once_with("test-tool")

    @patch('subprocess.run')
    def test_install_success(self, mock_run, mock_tool):
        """Test successful installation."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False
        mock_run.return_value.returncode = 0

        result = mock_tool.install(mock_registry, "/test/project")

        assert result is True
        mock_run.assert_called_once_with(["echo", "installing", "test-tool"], check=True)

    def test_install_already_installed(self, mock_tool):
        """Test installing tool that's already installed."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = True

        result = mock_tool.install(mock_registry)

        assert result is True

    @patch('subprocess.run')
    def test_install_failure(self, mock_run, mock_tool):
        """Test failed installation."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")

        result = mock_tool.install(mock_registry)

        assert result is False

    @patch('subprocess.run')
    def test_install_with_project_dir_placeholder(self, mock_run):
        """Test installation with project directory placeholder replacement."""
        # Create a tool with project_dir placeholder in install command
        tool_with_placeholder = MCPTool(
            name="test-tool",
            description="Test Tool with placeholder",
            prerequisite="python",
            error_message="Python not found",
            install_command=["echo", "installing", "in", "{project_dir}"]
        )

        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False

        result = tool_with_placeholder.install(mock_registry, "/custom/project")

        assert result is True
        # Verify the placeholder was replaced with the actual project directory
        mock_run.assert_called_once_with(["echo", "installing", "in", "/custom/project"], check=True)

    @patch('subprocess.run')
    def test_remove_success(self, mock_run, mock_tool):
        """Test successful removal."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = True
        mock_run.return_value.returncode = 0

        result = mock_tool.remove(mock_registry)

        assert result is True
        mock_run.assert_called_once_with(['claude', 'mcp', 'remove', 'test-tool'], check=True)

    def test_remove_not_installed(self, mock_tool):
        """Test removing tool that's not installed."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = False

        result = mock_tool.remove(mock_registry)

        assert result is True

    @patch('subprocess.run')
    def test_remove_failure(self, mock_run, mock_tool):
        """Test failed removal."""
        mock_registry = MagicMock()
        mock_registry.is_tool_installed.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")

        result = mock_tool.remove(mock_registry)

        assert result is False


class TestMCPToolRegistry:
    """Test cases for MCPToolRegistry class."""

    def test_init(self, mock_claude_mcp_calls):
        """Test registry initialization."""
        registry = MCPToolRegistry()
        assert isinstance(registry.tools, dict)
        assert len(registry.tools) > 0

        # Check that built-in tools are loaded
        assert "serena" in registry.tools
        assert "basic-memory" in registry.tools
        assert "gemini-cli" in registry.tools

    def test_get_tool_exists(self, mock_registry):
        """Test getting an existing tool."""
        tool = mock_registry.get_tool("test-tool")
        assert tool is not None
        assert tool.name == "test-tool"

    def test_get_tool_not_exists(self, mock_registry):
        """Test getting a non-existent tool."""
        tool = mock_registry.get_tool("nonexistent")
        assert tool is None

    def test_list_tools(self, mock_registry):
        """Test listing all tools."""
        tools = mock_registry.list_tools()
        assert len(tools) == 2
        assert "test-tool" in tools
        assert "another-tool" in tools

    def test_get_tool_names(self, mock_registry):
        """Test getting tool names."""
        names = mock_registry.get_tool_names()
        assert set(names) == {"test-tool", "another-tool"}

    @patch('claude_extend.tools.MCPTool.is_installed')
    def test_get_installed_tools(self, mock_is_installed, mock_registry):
        """Test getting installed tools."""
        # Mock test-tool as installed, another-tool as not installed
        mock_is_installed.side_effect = lambda *args, **kwargs: mock_is_installed.call_count == 1

        installed = mock_registry.get_installed_tools()
        assert installed == ["test-tool"]

    @patch('claude_extend.tools.MCPTool.is_installed')
    def test_get_available_tools(self, mock_is_installed, mock_registry):
        """Test getting available (not installed) tools."""
        # Mock test-tool as installed, another-tool as not installed
        mock_is_installed.side_effect = lambda *args, **kwargs: mock_is_installed.call_count == 1

        available = mock_registry.get_available_tools()
        assert available == ["another-tool"]


class TestMCPToolRegistryExternalConfig:
    """Test MCPToolRegistry with external configuration."""

    def test_load_tools_with_external_config(self, tmp_path, monkeypatch, mock_claude_mcp_calls):
        """Test loading tools from external config file."""
        from claude_extend.tools import MCPToolRegistry

        # Create external config
        config_data = {
            "tools": {
                "custom-tool": {
                    "name": "custom-tool",
                    "description": "Custom Tool - A custom MCP tool",
                    "prerequisite": "python",
                    "error_message": "Python not found",
                    "install_command": ["echo", "installing", "custom-tool"]
                }
            }
        }

        config_file = tmp_path / "tools.json"
        config_file.write_text(json.dumps(config_data))

        # Mock get_config_path to return our test config
        def mock_get_config_path():
            return config_file

        monkeypatch.setattr('claude_extend.utils.get_config_path', mock_get_config_path)

        # Create registry
        registry = MCPToolRegistry()

        # Should have our custom tool
        assert "custom-tool" in registry.tools
        assert registry.tools["custom-tool"].name == "custom-tool"
        assert registry.tools["custom-tool"].description == "Custom Tool - A custom MCP tool"

    def test_load_tools_external_config_failure_fallback(self, tmp_path, monkeypatch, capsys, mock_claude_mcp_calls):
        """Test fallback to defaults when external config fails."""
        from claude_extend.tools import MCPToolRegistry

        # Create invalid config file
        config_file = tmp_path / "tools.json"
        config_file.write_text("invalid json{")

        # Mock get_config_path to return our test config
        def mock_get_config_path():
            return config_file

        monkeypatch.setattr('claude_extend.utils.get_config_path', mock_get_config_path)

        # Create registry - should fall back to defaults
        registry = MCPToolRegistry()

        # Should have default tools
        assert "serena" in registry.tools
        assert "basic-memory" in registry.tools
        assert "gemini-cli" in registry.tools

        # Should show warning message
        captured = capsys.readouterr()
        assert "Failed to load or parse external config" in captured.err

    def test_load_tools_no_external_config(self, monkeypatch, mock_claude_mcp_calls):
        """Test loading with no external config (defaults only)."""
        from claude_extend.tools import MCPToolRegistry

        # Mock get_config_path to return None
        def mock_get_config_path():
            return None

        monkeypatch.setattr('claude_extend.utils.get_config_path', mock_get_config_path)

        # Create registry - should use defaults
        registry = MCPToolRegistry()

        # Should have default tools
        assert "serena" in registry.tools
        assert "basic-memory" in registry.tools
        assert "gemini-cli" in registry.tools
        assert len(registry.tools) == 3
