"""CLI entry point for python -m windbg_mcp."""

import argparse
import sys
from windbg_mcp.server import run_server


def main():
    """Main CLI entry point with stdio (default) and SSE transport support."""
    parser = argparse.ArgumentParser(description="WinDbgMCP Server CLI")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode for MCP protocol (default: stdio)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        help="Shortcut to run in SSE HTTP transport mode",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address for SSE server (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE server (default: 8000)",
    )

    args = parser.parse_args()

    transport_mode = "sse" if args.sse else args.transport
    run_server(transport=transport_mode, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
