#!/usr/bin/env python3
"""Verify work environment dependencies against Frappe v16 requirements."""

import argparse
import sys
from pathlib import Path

from env_checker.cli import main as cli_main
from env_checker.runner import load_config, run_checks

CONFIG_PATH = Path(__file__).resolve().parent / "versions.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check installed dependency versions against Frappe v16 requirements.",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Print results in the terminal instead of opening the GUI",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_PATH,
        help="Path to versions.json config file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.config.is_file():
        print(f"Config not found: {args.config}")
        sys.exit(1)

    config = load_config(args.config)
    results = run_checks(config)

    if args.cli:
        cli_main(results)
    else:
        try:
            from env_checker.gui import main as gui_main
        except ImportError:
            print("tkinter is required for the GUI. On Debian/Ubuntu: sudo apt install python3-tk")
            print("Use --cli for terminal output.")
            sys.exit(1)
        gui_main(config, args.config.parent)


if __name__ == "__main__":
    main()
