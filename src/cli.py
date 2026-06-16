from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, Prompt

from src.tsv_manager import load_tsv, get_pending_emails

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bulk-email-sender",
        description="Send bulk emails from a TSV file with progress tracking and Discord notifications.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to the TSV file containing emails",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=None,
        help="Number of emails to send (default: all pending)",
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test SMTP connection and exit",
    )
    parser.add_argument(
        "--no-discord",
        action="store_true",
        help="Skip Discord notification after completion",
    )
    parser.add_argument(
        "-a",
        "--after",
        choices=["close", "continue"],
        default=None,
        help="Action after batch: 'close' to exit, 'continue' to prompt for next batch",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive prompts, use CLI arguments only",
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default=None,
        help="Path to .env file (default: .env in current directory)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between emails in seconds (default: 0)",
    )
    return parser


def _validate_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        sys.exit(1)
    if not path.suffix.lower() == ".tsv":
        console.print(
            f"[yellow]Warning:[/yellow] File does not have .tsv extension: {path}"
        )
    return str(path)


def interactive_mode() -> dict:
    console.print("\n[bold cyan]Bulk Email Sender - Interactive Mode[/bold cyan]\n")

    file_path = Prompt.ask("Path to TSV file")
    file_path = _validate_file(file_path)

    data = load_tsv(file_path)
    pending = get_pending_emails(data)
    console.print(
        f"Found [green]{len(pending)}[/green] pending emails out of {len(data)} total.\n"
    )

    count_str = Prompt.ask(
        "How many emails to send?",
        default=str(len(pending)),
    )
    try:
        count = int(count_str)
    except ValueError:
        console.print("[red]Invalid number.[/red] Using all pending emails.")
        count = len(pending)

    if count > len(pending):
        console.print(
            f"[yellow]Requested {count} but only {len(pending)} pending. Using {len(pending)}.[/yellow]"
        )
        count = len(pending)

    delay = float(Prompt.ask("Delay between emails (seconds)", default="0"))

    no_discord = not Confirm.ask("Send stats to Discord?", default=True)

    after = None
    if not Confirm.ask("After batch finishes, close the app?", default=True):
        after = "continue"

    return {
        "file": file_path,
        "count": count,
        "delay": delay,
        "no_discord": no_discord,
        "after": after,
        "no_interactive": False,
        "env_file": None,
        "test_connection": False,
    }


def parse_args() -> dict:
    parser = build_parser()
    args = parser.parse_args()

    if args.no_interactive or args.test_connection or args.file:
        if not args.file and not args.test_connection:
            console.print(
                "[red]Error:[/red] --file is required in non-interactive mode."
            )
            sys.exit(1)

        file_path = _validate_file(args.file) if args.file else None

        return {
            "file": file_path,
            "count": args.count,
            "delay": args.delay,
            "no_discord": args.no_discord,
            "after": args.after,
            "no_interactive": args.no_interactive,
            "env_file": args.env_file,
            "test_connection": args.test_connection,
        }

    return interactive_mode()
