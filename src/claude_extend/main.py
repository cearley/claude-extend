#!/usr/bin/env python3
"""Claude eXtend (cx) - CLI tool for managing MCP server connections with Claude Code."""

import sys


def main():
    """Main entry point for the cx CLI tool."""
    print("Claude eXtend (cx) - MCP Server Manager")
    print("Version 0.1.0")
    print()
    print("Available commands:")
    print("  list    - List connected MCP servers")
    print("  link    - Link an MCP server to Claude Code")
    print("  unlink  - Unlink an MCP server from Claude Code")
    print("  help    - Show this help message")

    # TODO: Implement actual CLI functionality
    if len(sys.argv) > 1:
        command = sys.argv[1]
        print(f"\nCommand '{command}' not yet implemented.")
    else:
        print("\nUse 'cx help' for usage information.")


if __name__ == '__main__':
    main()
