from __future__ import annotations

import csv
from pathlib import Path


EXPECTED_COLUMNS = ["id", "email", "subject", "body", "status"]

VALID_STATUSES = {"pending", "sent", "error"}


def load_tsv(file_path: str | Path) -> list[dict[str, str]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"TSV file not found: {path}")

    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError("TSV file is empty or has no headers")

        missing = set(EXPECTED_COLUMNS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"TSV missing columns: {', '.join(sorted(missing))}")

        for i, row in enumerate(rows := list(reader), start=2):
            row["id"] = row.get("id", "").strip()
            row["email"] = row.get("email", "").strip()
            row["subject"] = row.get("subject", "").strip()
            row["body"] = row.get("body", "").strip()
            row["status"] = row.get("status", "pending").strip().lower()
            if not row["id"]:
                raise ValueError(f"Row {i}: 'id' is empty")
            if not row["email"] or "@" not in row["email"]:
                raise ValueError(f"Row {i}: invalid email '{row['email']}'")

    return rows


def save_tsv(file_path: str | Path, data: list[dict[str, str]]) -> None:
    path = Path(file_path)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED_COLUMNS, delimiter="\t")
        writer.writeheader()
        writer.writerows(data)


def get_pending_emails(data: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in data if row["status"] == "pending"]


def update_status(data: list[dict[str, str]], row_id: str, status: str) -> bool:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {VALID_STATUSES}")

    for row in data:
        if row["id"] == row_id:
            row["status"] = status
            return True
    return False


def get_stats(data: list[dict[str, str]]) -> dict[str, int | list[dict[str, str]]]:
    total = len(data)
    sent = sum(1 for r in data if r["status"] == "sent")
    pending = sum(1 for r in data if r["status"] == "pending")
    errors = [r for r in data if r["status"] == "error"]
    return {
        "total": total,
        "sent": sent,
        "pending": pending,
        "error": len(errors),
        "error_details": errors,
    }
