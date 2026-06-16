from __future__ import annotations

import time

from rich.console import Console
from rich.prompt import Confirm, Prompt

from src.cli import parse_args
from src.config import load_config, validate_email_config, validate_discord_config
from src.discord_webhook import send_stats_to_discord
from src.email_sender import send_email, test_connection
from src.progress import EmailProgress
from src.tsv_manager import (
    get_pending_emails,
    get_stats,
    load_tsv,
    save_tsv,
    update_status,
)

console = Console()


def run_batch(
    config,
    file_path: str,
    count: int | None,
    delay: float,
    no_discord: bool,
) -> dict:
    data = load_tsv(file_path)
    pending = get_pending_emails(data)

    if not pending:
        console.print("[yellow]No pending emails to send.[/yellow]")
        return get_stats(data)

    to_send = pending[:count] if count else pending
    console.print(f"\n[green]Sending {len(to_send)} emails...[/green]\n")

    progress = EmailProgress()
    progress.start(len(to_send))

    start_time = time.time()

    for i, row in enumerate(to_send):
        success, error_msg = send_email(
            config, row["email"], row["subject"], row["body"]
        )

        if success:
            update_status(data, row["id"], "sent")
        else:
            update_status(data, row["id"], "error")
            console.print(f"\n[red]Error sending to {row['email']}:[/red] {error_msg}")

        progress.update(row["email"], success, i + 1)
        save_tsv(file_path, data)

        if delay > 0 and i < len(to_send) - 1:
            time.sleep(delay)

    duration = time.time() - start_time
    stats = get_stats(data)
    save_tsv(file_path, data)
    progress.finish(stats, duration)

    if not no_discord:
        send_stats_to_discord(config, stats, duration)

    return stats


def post_batch_prompt() -> str:
    console.print()
    if Confirm.ask("[bold]Batch complete![/bold] Close the app?", default=True):
        return "close"
    return "continue"


def main() -> None:
    try:
        args = parse_args()
        config = load_config(args.get("env_file"))

        if args.get("test_connection"):
            console.print("\n[bold]Testing SMTP connection...[/bold]")
            ok, msg = test_connection(config)
            if ok:
                console.print(f"[green]{msg}[/green]")
            else:
                console.print(f"[red]{msg}[/red]")
            return

        valid, msg = validate_email_config(config)
        if not valid:
            console.print(f"[red]Config error:[/red] {msg}")
            return

        if not args.get("no_discord"):
            dc_ok, dc_msg = validate_discord_config(config)
            if not dc_ok:
                console.print(f"[yellow]Discord:[/yellow] {dc_msg}")

        while True:
            stats = run_batch(
                config,
                args["file"],
                args.get("count"),
                args.get("delay", 0.0),
                args.get("no_discord", False),
            )

            after = args.get("after")
            if after == "close" or (after is None and args.get("no_interactive")):
                break
            elif after == "continue":
                pending = get_pending_emails(load_tsv(args["file"]))
                if not pending:
                    console.print("[yellow]No more pending emails.[/yellow]")
                    break
                console.print(
                    f"\n[yellow]{len(pending)} emails still pending.[/yellow]"
                )
                count_str = Prompt.ask(
                    "How many to send next? (or 'q' to quit)",
                    default="q",
                )
                if count_str.lower() == "q":
                    break
                try:
                    args["count"] = int(count_str)
                except ValueError:
                    console.print("[red]Invalid number.[/red]")
                    break
            else:
                action = post_batch_prompt()
                if action == "close":
                    break
                pending = get_pending_emails(load_tsv(args["file"]))
                if not pending:
                    console.print("[yellow]No more pending emails.[/yellow]")
                    break
                console.print(
                    f"\n[yellow]{len(pending)} emails still pending.[/yellow]"
                )
                count_str = Prompt.ask(
                    "How many to send next? (or 'q' to quit)",
                    default="q",
                )
                if count_str.lower() == "q":
                    break
                try:
                    args["count"] = int(count_str)
                except ValueError:
                    console.print("[red]Invalid number.[/red]")
                    break

        console.print("\n[bold green]Done![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Unexpected error:[/red] {e}")
        raise
