"""MCP Tool Registry and Management."""

import os
import shutil
import subprocess
from typing import Dict, List, Optional

from .utils import print_message


class MCPTool:

    def __init__(self, name: str, description: str, command: str, args: List[str]):
        self.name = name
        self.description = description
        self.command = command
        self.args = args

    def check_prerequisites(self) -> bool:
        return bool(shutil.which(self.command))

    def is_installed(self, registry) -> bool:
        return registry.is_tool_installed(self.name)

    def _run_claude_command(self, command: List[str], action: str) -> bool:
        try:
            subprocess.run(command, check=True)
            print_message('success', f"{self.name} {action}")
            return True
        except subprocess.CalledProcessError:
            print_message('error', f"Failed to {action} {self.name}")
            return False

    def install(self, registry, project_dir: str = None) -> bool:
        if project_dir is None:
            project_dir = os.getcwd()

        if self.is_installed(registry=registry):
            print_message('success', f"{self.name} is already installed")
            return True

        print_message('info', f"Installing {self.description}...")

        processed_args = [arg.replace('{project_dir}', project_dir) for arg in self.args]

        command = ['claude', 'mcp', 'add', self.name, '--', self.command] + processed_args
        return self._run_claude_command(command, "installed")

    def remove(self, registry) -> bool:
        if not self.is_installed(registry=registry):
            print_message('info', f"{self.name} is not installed")
            return True

        print_message('info', f"Removing {self.description}...")

        command = ['claude', 'mcp', 'remove', self.name]
        return self._run_claude_command(command, "removed")

    def to_claude_desktop_format(self) -> dict:
        return {
            "command": self.command,
            "args": self.args
        }


class MCPToolRegistry:

    def __init__(self):
        self.tools = self._load_tools()
        self._installed_tools_cache = None

    @staticmethod
    def _load_tools() -> Dict[str, MCPTool]:
        from .utils import get_config_path, load_external_tools_config, print_message

        config_path = get_config_path()
        if config_path:
            try:
                external_tools = load_external_tools_config(config_path)
                print_message('info', f"Loaded tools from config: {config_path}")

                tools = {}
                for tool_name, tool_config in external_tools.items():
                    tools[tool_name] = MCPTool(
                        name=tool_name,
                        description=tool_config['description'],
                        command=tool_config['command'],
                        args=tool_config['args']
                    )
                return tools

            except Exception:
                print_message('warning', f"Failed to load or parse external config at '{config_path}'.")
                print_message('info', "Please ensure the file exists, is valid JSON, and has correct permissions.")
                print_message('info', "Falling back to default tool registry")

        tools = {}

        tool_configs = {
            'serena': {
                'description': 'Semantic code analysis and intelligent IDE assistant',
                'command': 'uvx',
                'args': ['--from', 'git+https://github.com/oraios/serena', 'serena', 'start-mcp-server',
                         '--context', 'ide-assistant', '--project', '{project_dir}']
            },
            'basic-memory': {
                'description': 'Enhanced memory capabilities for Claude',
                'command': 'basic-memory',
                'args': ['mcp']
            },
            'gemini-cli': {
                'description': 'Google Gemini integration tool',
                'command': 'npx',
                'args': ['-y', 'gemini-mcp-tool']
            }
        }

        for tool_name, config in tool_configs.items():
            tools[tool_name] = MCPTool(
                name=tool_name,
                description=config['description'],
                command=config['command'],
                args=config['args']
            )

        return tools

    def _get_installed_tools_output(self) -> Optional[str]:
        if self._installed_tools_cache is None:
            try:
                result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
                if result.returncode == 0:
                    self._installed_tools_cache = result.stdout
                else:
                    self._installed_tools_cache = ""
            except subprocess.SubprocessError:
                self._installed_tools_cache = ""
        return self._installed_tools_cache

    def is_tool_installed(self, tool_name: str) -> bool:
        installed_output = self._get_installed_tools_output()
        return f"{tool_name}:" in installed_output if installed_output else False

    def get_tool(self, name: str) -> Optional[MCPTool]:
        return self.tools.get(name)

    def list_tools(self) -> Dict[str, MCPTool]:
        return self.tools

    def get_tool_names(self) -> List[str]:
        return list(self.tools.keys())

    def get_installed_tools(self) -> List[str]:
        return [name for name, tool in self.tools.items() if tool.is_installed(registry=self)]

    def get_available_tools(self) -> List[str]:
        return [name for name, tool in self.tools.items() if not tool.is_installed(registry=self)]
