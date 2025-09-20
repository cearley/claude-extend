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
        print(f"{status}  {name} - {tool.description}")
        if not tool.check_prerequisites():
            print_message('warning', f"   Prerequisites missing: {tool.error_message}")
        print()

    print(f"Total: {len(tools)} tools ({len(installed)} installed)")
    print()
    print("💡 Tip: Use 'cx add --interactive' for guided tool selection and installation")


def cmd_add(args, registry: MCPToolRegistry) -> None:
    """Add MCP tools."""
    if args.interactive:
        return cmd_add_interactive(args, registry)

    if not args.tools:
        print_message('error', "No tools specified. Use --interactive or specify tool names.")
        return

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

def cmd_remove(args, registry: MCPToolRegistry) -> None:
    """Remove MCP tools."""
    if not args.tools:
        print_message('error', "No tools specified. Specify tool names to remove.")
        return

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

def _get_user_tool_selection(tools: dict, registry: MCPToolRegistry) -> list:
    """Get tool selection from user through interactive checkbox interface."""
    import questionary

    # Create choices for ALL tools (not just available ones)
    choices = []
    for name, tool in tools.items():
        description = f"{name} - {tool.description}"

        # Add status indicators
        if tool.is_installed(registry=registry):
            description += " (already installed)"
        elif not tool.check_prerequisites():
            description += " ⚠️  (prerequisites missing)"

        choices.append(questionary.Choice(title=description, value=name))

    # Show interactive checkbox interface
    try:
        selected = questionary.checkbox(
            "Select MCP tools to install:",
            choices=choices,
            instruction="(Use arrow keys to navigate, space to select, enter to confirm, ctrl+c to cancel)"
        ).ask()

        # questionary returns None if user cancels/quits (Ctrl+C or ESC)
        if selected is None:
            print_message('info', "Installation cancelled.")
            return []

        # Filter out already installed tools from the selection
        filtered_selected = []
        for tool_name in selected:
            tool = tools[tool_name]
            if tool.is_installed(registry=registry):
                print_message('info', f"{tool_name} is already installed, skipping.")
            else:
                filtered_selected.append(tool_name)

        return filtered_selected

    except KeyboardInterrupt:
        print_message('info', "Installation cancelled.")
        return []

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

    selected_tools = _get_user_tool_selection(tools, registry)
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
    add_parser = subparsers.add_parser('add', help='Add MCP tools (use --interactive for guided selection)')
    add_parser.add_argument('tools', nargs='*', help='Tool names to install')
    add_parser.add_argument('--interactive', '-i', action='store_true',
                            help='Interactive tool selection menu')

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
