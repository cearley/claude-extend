#!/usr/bin/env python3
"""Claude eXtend (cx) - CLI tool for managing MCP server connections with Claude Code."""

import argparse
import sys

from . import __version__
from .tools import MCPToolRegistry
from .utils import print_message, validate_environment, validate_interactive_environment


def cmd_list(_args, registry: MCPToolRegistry) -> None:
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
            print_message('warning', f"   Prerequisites missing: {tool.command} not found. Please install {tool.command} first.")
        print()

    print(f"Total: {len(tools)} tools ({len(installed)} installed)")
    print()
    print("💡 Tip: Use 'cx add --interactive' or 'cx remove --interactive' for guided tool management")


def cmd_add(args, registry: MCPToolRegistry) -> None:
    if args.interactive:
        return cmd_add_interactive(args, registry)

    if not args.tools:
        print_message('error', "No tools specified. Use --interactive or specify tool names.")
        return

    if not validate_environment():
        sys.exit(1)

    tools = registry.list_tools()
    _process_tools(args.tools, tools, registry, "install", lambda tool, **kwargs: tool.install(**kwargs))

def cmd_remove(args, registry: MCPToolRegistry) -> None:
    if args.interactive:
        return cmd_remove_interactive(args, registry)

    if not args.tools:
        print_message('error', "No tools specified. Use --interactive or specify tool names to remove.")
        return

    if not validate_environment():
        sys.exit(1)

    tools = registry.list_tools()
    _process_tools(args.tools, tools, registry, "remove", lambda tool, **kwargs: tool.remove(**kwargs))

def _get_user_tool_selection(
    tools: dict,
    registry: MCPToolRegistry,
    prompt: str,
    filter_func,
    cancel_message: str = "Operation cancelled."
) -> list:
    import questionary

    choices = []
    for name, tool in tools.items():
        description = f"{name} - {tool.description}"

        is_installed = tool.is_installed(registry=registry)
        if is_installed:
            description += " (already installed)"
        elif not tool.check_prerequisites():
            description += " ⚠️  (prerequisites missing)"
        else:
            description += " (not installed)" if "remove" in prompt.lower() else ""

        choices.append(questionary.Choice(title=description, value=name))

    try:
        selected = questionary.checkbox(
            prompt,
            choices=choices,
            instruction="(Use arrow keys to navigate, space to select, enter to confirm, ctrl+c to cancel)"
        ).ask()

        if selected is None:
            print_message('info', cancel_message)
            return []

        filtered_selected = []
        for tool_name in selected:
            tool = tools[tool_name]
            if filter_func(tool, registry):
                filtered_selected.append(tool_name)
            else:
                status = "is already installed" if "install" in prompt.lower() else "is not installed"
                print_message('info', f"{tool_name} {status}, skipping.")

        return filtered_selected

    except KeyboardInterrupt:
        print_message('info', cancel_message)
        return []

def _process_tools(tool_names: list, tools: dict, registry: MCPToolRegistry, action_name: str, action_func) -> None:
    print_message('info', f"{action_name.capitalize()}ing {len(tool_names)} MCP tool(s)...")
    print()

    for tool_name in tool_names:
        tool = tools.get(tool_name)
        if not tool:
            print_message('error', f"Unknown tool: {tool_name}")
            print_message('info', f"Available tools: {', '.join(tools.keys())}")
            continue

        print_message('info', f"Processing: {tool.description}")

        if action_name == "install" and not tool.check_prerequisites():
            print_message('error', f"Prerequisites not met for {tool_name}. {tool.command} not found. Please install {tool.command} first.")
            print_message('error', f"✗ Failed to {action_name} {tool_name}")
        elif action_func(tool, registry=registry):
            past_tense = "installed" if action_name == "install" else "removed"
            print_message('success', f"✓ {tool_name} {past_tense} successfully")
        else:
            print_message('error', f"✗ Failed to {action_name} {tool_name}")
        print()

    completion_word = "installation" if action_name == "install" else "removal"
    print_message('success', f"MCP tool {completion_word} complete!")


def cmd_add_interactive(_args, registry: MCPToolRegistry) -> None:
    if not validate_interactive_environment():
        sys.exit(1)

    tools = registry.list_tools()
    available_tools = registry.get_available_tools()

    if not available_tools:
        print_message('success', "All tools are already installed!")
        return

    selected_tools = _get_user_tool_selection(
        tools, 
        registry, 
        "Select MCP tools to install:",
        lambda tool, reg: not tool.is_installed(registry=reg),
        "Installation cancelled."
    )
    if not selected_tools:
        return

    _process_tools(selected_tools, tools, registry, "install", lambda tool, **kwargs: tool.install(**kwargs))


def cmd_remove_interactive(_args, registry: MCPToolRegistry) -> None:
    if not validate_interactive_environment():
        sys.exit(1)

    tools = registry.list_tools()
    installed_tools = registry.get_installed_tools()

    if not installed_tools:
        print_message('info', "No tools are currently installed.")
        return

    selected_tools = _get_user_tool_selection(
        tools, 
        registry, 
        "Select MCP tools to remove:",
        lambda tool, reg: tool.is_installed(registry=reg),
        "Removal cancelled."
    )
    if not selected_tools:
        return

    _process_tools(selected_tools, tools, registry, "remove", lambda tool, **kwargs: tool.remove(**kwargs))


def main():
    parser = argparse.ArgumentParser(
        description="Claude eXtend (cx) - MCP Server Manager",
        prog="cx"
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    subparsers.add_parser('list', help='List available MCP tools')

    add_parser = subparsers.add_parser('add', help='Add MCP tools (use --interactive for guided selection)')
    add_parser.add_argument('tools', nargs='*', help='Tool names to install')
    add_parser.add_argument('--interactive', '-i', action='store_true',
                            help='Interactive tool selection menu')

    remove_parser = subparsers.add_parser('remove', help='Remove MCP tools (use --interactive for guided selection)')
    remove_parser.add_argument('tools', nargs='*', help='Tool names to remove')
    remove_parser.add_argument('--interactive', '-i', action='store_true',
                              help='Interactive tool removal menu')

    args = parser.parse_args()

    registry = MCPToolRegistry()

    if args.command == 'list':
        cmd_list(args, registry)
    elif args.command == 'add':
        cmd_add(args, registry)
    elif args.command == 'remove':
        cmd_remove(args, registry)
    else:
        print("Claude eXtend (cx) - MCP Server Manager")
        print(f"Version {__version__}")
        print()
        parser.print_help()


if __name__ == '__main__':
    main()
