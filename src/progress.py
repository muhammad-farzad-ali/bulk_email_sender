from __future__ import annotations

import time

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table


class EmailProgress:
    def __init__(self) -> None:
        self.console = Console()
        self.start_time: float = 0.0
        self.sent = 0
        self.failed = 0
        self.total = 0
        self._progress: Progress | None = None
        self._task_id = None

    def start(self, total: int) -> None:
        self.total = total
        self.sent = 0
        self.failed = 0
        self.start_time = time.time()

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console,
        )
        self._progress.start()
        self._task_id = self._progress.add_task("Sending emails", total=total)

    def update(self, email: str, success: bool, current: int) -> None:
        if success:
            self.sent += 1
        else:
            self.failed += 1

        if self._progress and self._task_id is not None:
            self._progress.update(
                self._task_id, advance=1, description=f"Sending to {email}"
            )

    def stop(self) -> None:
        if self._progress:
            self._progress.stop()
            self._progress = None

    def finish(self, stats: dict, duration: float) -> None:
        self.stop()

        table = Table(
            title="📧 Send Report", show_header=True, header_style="bold cyan"
        )
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right")

        table.add_row("Total", str(stats["total"]))
        table.add_row("Sent", f"[green]{stats['sent']}[/green]")
        table.add_row("Failed", f"[red]{stats['error']}[/red]")
        table.add_row("Pending", str(stats["pending"]))

        minutes = int(duration // 60)
        seconds = duration % 60
        if minutes > 0:
            dur_str = f"{minutes}m {seconds:.0f}s"
        else:
            dur_str = f"{seconds:.1f}s"
        table.add_row("Duration", dur_str)

        if stats["sent"] > 0:
            avg = duration / stats["sent"]
            table.add_row("Avg/Email", f"{avg:.1f}s")

        self.console.print()
        self.console.print(table)
