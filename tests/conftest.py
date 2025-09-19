"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
from claude_extend.tools import MCPTool, MCPToolRegistry


@pytest.fixture
def mock_tool():
    """Create a mock MCP tool for testing."""
    return MCPTool(
        name="test-tool",
        description="Test Tool - A tool for testing",
        prerequisite="python",
        error_message="Python not found",
        install_command=["echo", "installing", "test-tool"]
    )


@pytest.fixture
def mock_registry():
    """Create a mock registry with test tools."""
    registry = MCPToolRegistry()
    # Replace with test tools
    registry.tools = {
        "test-tool": MCPTool(
            name="test-tool",
            description="Test Tool - A tool for testing",
            prerequisite="python",
            error_message="Python not found",
            install_command=["echo", "installing", "test-tool"]
        ),
        "another-tool": MCPTool(
            name="another-tool",
            description="Another Tool - Another testing tool",
            prerequisite="node",
            error_message="Node.js not found",
            install_command=["echo", "installing", "another-tool"]
        )
    }
    return registry


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls."""
    with patch('subprocess.run') as mock:
        mock.return_value.stdout = ""
        mock.return_value.returncode = 0
        yield mock


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which to control prerequisite checking."""
    with patch('shutil.which') as mock:
        # By default, assume all prerequisites are available
        mock.return_value = "/usr/bin/mock-command"
        yield mock