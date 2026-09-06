"""CLI entry point for python -m windbg_mcp."""

import sys
from windbg_mcp.server import run_server


def main():
    """Main CLI entry point."""
    run_server()


if __name__ == "__main__":
    main()
