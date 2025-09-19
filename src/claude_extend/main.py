#!/usr/bin/env python3
"""Claude eXtend (cx) - CLI tool for managing MCP server connections with Claude Code."""

import argparse
import sys

from . import __version__
from .tools import MCPToolRegistry
from .utils import print_message, validate_environment, validate_interactive_environment


def cmd_list(_args, registry: MCPToolRegistry) -> None:
    """List available MCP tools."""
    tools = registry.list_tools()
    installed = registry.get_installed_tools()

    print("🔧 Available MCP Tools")
    print("======================")
    print()

    if not tools:
        print_message('info', "No tools available in registry.")
        return

    for name, tool in tools.items():
        status = "✅ INSTALLED" if name in installed else "⭕ AVAILABLE"
        print(f"{status}  {tool.description}")
        if not tool.check_prerequisites():
            print_message('warning', f"   Prerequisites missing: {tool.error_message}")
        print()

    print(f"Total: {len(tools)} tools ({len(installed)} installed)")


def cmd_add(args, registry: MCPToolRegistry) -> None:
    """Add MCP tools."""
    if args.interactive:
        return cmd_add_interactive(args, registry)

    if not args.tools:
        print_message('error', "No tools specified. Use --interactive or specify tool names.")
        return None

    if not validate_environment():
        sys.exit(1)

    for tool_name in args.tools:
        tool = registry.get_tool(tool_name)
        if not tool:
            print_message('error', f"Unknown tool: {tool_name}")
            print_message('info', f"Available tools: {', '.join(registry.get_tool_names())}")
            continue

        print_message('info', f"Processing: {tool.description}")

        if not tool.check_prerequisites():
            print_message('error', f"Prerequisites not met for {tool_name}. {tool.error_message}")
            print_message('error', f"✗ Failed to install {tool_name}")
        elif tool.install(registry=registry):
            print_message('success', f"✓ {tool_name} installed successfully")
        else:
            print_message('error', f"✗ Failed to install {tool_name}")
        print()
    return None

def cmd_remove(args, registry: MCPToolRegistry) -> None:
    """Remove MCP tools."""
    if not args.tools:
        print_message('error', "No tools specified. Specify tool names to remove.")
        return None

    if not validate_environment():
        sys.exit(1)

    for tool_name in args.tools:
        tool = registry.get_tool(tool_name)
        if not tool:
            print_message('error', f"Unknown tool: {tool_name}")
            print_message('info', f"Available tools: {', '.join(registry.get_tool_names())}")
            continue

        print_message('info', f"Processing: {tool.description}")

        if tool.remove(registry=registry):
            print_message('success', f"✓ {tool_name} removed successfully")
        else:
            print_message('error', f"✗ Failed to remove {tool_name}")
        print()
    return None


def _display_tool_menu(tools: dict, tool_list: list, registry: MCPToolRegistry) -> None:
    """Display the interactive tool selection menu."""
    print(file=sys.stderr)
    print_message('info', "Available MCP Tools:")
    print(file=sys.stderr)

    for i, name in enumerate(tool_list, 1):
        tool = tools[name]
        status = " (installed)" if tool.is_installed(registry=registry) else ""
        print(f"  {i}) {tool.description}{status}", file=sys.stderr)

    print("  a) Install all available tools", file=sys.stderr)
    print("  q) Quit", file=sys.stderr)
    print(file=sys.stderr)


def _parse_selection(selection: str, tool_list: list, available_tools: list) -> list:
    """Parse user selection and return list of selected tool names."""
    if selection.lower() == 'q':
        return ['__quit__']
    elif selection.lower() == 'a':
        return available_tools

    selected = []
    for sel in selection.split(','):
        try:
            idx = int(sel.strip()) - 1
            if 0 <= idx < len(tool_list):
                tool_name = tool_list[idx]
                if tool_name in available_tools:
                    selected.append(tool_name)
                else:
                    print_message('warning', f"{tool_name} is already installed")
            else:
                print_message('warning', f"Invalid selection: {sel.strip()}")
        except ValueError:
            print_message('warning', f"Invalid input: {sel.strip()}")

    return selected


def _get_user_tool_selection(tools: dict, available_tools: list, registry: MCPToolRegistry) -> list:
    """Get tool selection from user through interactive menu."""
    tool_list = list(tools.keys())

    while True:
        _display_tool_menu(tools, tool_list, registry)
        selection = input("Select tools to install (comma-separated numbers, 'a' for all, 'q' to quit): ")

        selected = _parse_selection(selection, tool_list, available_tools)

        if selected == ['__quit__']:
            print_message('info', "Goodbye!")
            return []
        elif selected:
            return selected


def _install_selected_tools(selected_tools: list, tools: dict, registry: MCPToolRegistry) -> None:
    """Install the selected tools."""
    print_message('info', f"Installing {len(selected_tools)} MCP tool(s)...")
    print()

    for tool_name in selected_tools:
        tool = tools[tool_name]
        print_message('info', f"Processing: {tool.description}")

        if not tool.check_prerequisites():
            print_message('error', f"Prerequisites not met for {tool_name}. {tool.error_message}")
            print_message('error', f"✗ Failed to install {tool_name}")
        elif tool.install(registry=registry):
            print_message('success', f"✓ {tool_name} installed successfully")
        else:
            print_message('error', f"✗ Failed to install {tool_name}")
        print()

    print_message('success', "MCP tool installation complete!")


def cmd_add_interactive(_args, registry: MCPToolRegistry) -> None:
    """Interactive tool selection and installation."""
    if not validate_interactive_environment():
        sys.exit(1)

    tools = registry.list_tools()
    available_tools = registry.get_available_tools()

    if not available_tools:
        print_message('success', "All tools are already installed!")
        return

    selected_tools = _get_user_tool_selection(tools, available_tools, registry)
    if not selected_tools:
        return

    _install_selected_tools(selected_tools, tools, registry)


def main():
    """Main entry point for the cx CLI tool."""
    parser = argparse.ArgumentParser(
        description="Claude eXtend (cx) - MCP Server Manager",
        prog="cx"
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # List command
    subparsers.add_parser('list', help='List available MCP tools')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add MCP tools')
    add_parser.add_argument('tools', nargs='*', help='Tool names to install')
    add_parser.add_argument('--interactive', '-i', action='store_true',
                           help='Interactive tool selection')

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove MCP tools')
    remove_parser.add_argument('tools', nargs='*', help='Tool names to remove')

    # Parse arguments
    args = parser.parse_args()

    # Initialize registry
    registry = MCPToolRegistry()

    # Route to appropriate command
    if args.command == 'list':
        cmd_list(args, registry)
    elif args.command == 'add':
        cmd_add(args, registry)
    elif args.command == 'remove':
        cmd_remove(args, registry)
    else:
        # Show help if no command provided
        print("Claude eXtend (cx) - MCP Server Manager")
        print(f"Version {__version__}")
        print()
        parser.print_help()


if __name__ == '__main__':
    main()
