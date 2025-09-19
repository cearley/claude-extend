"""MCP Tool Registry and Management."""

import os
import subprocess
import shutil
from typing import Dict, List, Tuple, Optional
from .utils import print_message


class MCPTool:
    """Represents an MCP tool with its configuration."""

    def __init__(self, name: str, description: str, prerequisite: str,
                 error_message: str, install_command: List[str]):
        self.name = name
        self.description = description
        self.prerequisite = prerequisite
        self.error_message = error_message
        self.install_command = install_command

    def check_prerequisites(self) -> bool:
        """Check if tool prerequisites are met."""
        if self.prerequisite == 'npm':
            return bool(shutil.which('npm') or shutil.which('npx'))
        return bool(shutil.which(self.prerequisite))

    def is_installed(self) -> bool:
        """Check if MCP tool already exists in config."""
        try:
            result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
            return f"{self.name}:" in result.stdout
        except subprocess.SubprocessError:
            return False

    def install(self, project_dir: str = None) -> bool:
        """Install this MCP tool."""
        if project_dir is None:
            project_dir = os.getcwd()

        if self.is_installed():
            print_message('success', f"{self.name} is already installed")
            return True

        print_message('info', f"Installing {self.description}...")

        try:
            # Replace {project_dir} placeholder with actual path
            command = [cmd.replace('{project_dir}', project_dir) for cmd in self.install_command]
            subprocess.run(command, check=True)
            print_message('success', f"{self.name} installed")
            return True
        except subprocess.CalledProcessError:
            print_message('error', f"Failed to install {self.name}")
            return False


class MCPToolRegistry:
    """Registry of available MCP tools."""

    def __init__(self):
        self.tools = self._load_tools()

    def _load_tools(self) -> Dict[str, MCPTool]:
        """Load the registry of available MCP tools."""
        return {
            'serena': MCPTool(
                name='serena',
                description='Serena - Semantic code analysis and intelligent IDE assistant',
                prerequisite='uvx',
                error_message='uvx not found. Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh',
                install_command=['claude', 'mcp', 'add', 'serena', '--', 'uvx', '--from',
                               'git+https://github.com/oraios/serena', 'serena', 'start-mcp-server',
                               '--context', 'ide-assistant', '--project', '{project_dir}']
            ),
            'basic-memory': MCPTool(
                name='basic-memory',
                description='Basic Memory - Enhanced memory capabilities for Claude',
                prerequisite='basic-memory',
                error_message='basic-memory not found. Please install it first. See: https://docs.basicmemory.com/integrations/claude-code/',
                install_command=['claude', 'mcp', 'add', 'basic-memory', 'basic-memory', 'mcp']
            ),
            'gemini-cli': MCPTool(
                name='gemini-cli',
                description='Gemini CLI - Google Gemini integration tool',
                prerequisite='npm',
                error_message='npm/npx not found. Please install Node.js first.',
                install_command=['claude', 'mcp', 'add', 'gemini-cli', '--', 'npx', '-y', 'gemini-mcp-tool']
            )
        }

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> Dict[str, MCPTool]:
        """Get all available tools."""
        return self.tools

    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return list(self.tools.keys())

    def get_installed_tools(self) -> List[str]:
        """Get list of currently installed tool names."""
        return [name for name, tool in self.tools.items() if tool.is_installed()]

    def get_available_tools(self) -> List[str]:
        """Get list of available but not installed tool names."""
        return [name for name, tool in self.tools.items() if not tool.is_installed()]