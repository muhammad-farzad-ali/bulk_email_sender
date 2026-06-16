import pytest
from pathlib import Path

from src.tsv_manager import (
    EXPECTED_COLUMNS,
    get_pending_emails,
    get_stats,
    load_tsv,
    save_tsv,
    update_status,
)


def _write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("\t".join(EXPECTED_COLUMNS) + "\n")
        for row in rows:
            f.write("\t".join(row.get(col, "") for col in EXPECTED_COLUMNS) + "\n")


class TestLoadTsv:
    def test_valid_file(self, tmp_path: Path) -> None:
        tsv = tmp_path / "test.tsv"
        _write_tsv(
            tsv,
            [
                {
                    "id": "1",
                    "email": "a@test.com",
                    "subject": "Hi",
                    "body": "Hello",
                    "status": "pending",
                },
                {
                    "id": "2",
                    "email": "b@test.com",
                    "subject": "Bye",
                    "body": "Goodbye",
                    "status": "sent",
                },
            ],
        )
        data = load_tsv(tsv)
        assert len(data) == 2
        assert data[0]["email"] == "a@test.com"
        assert data[1]["status"] == "sent"

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_tsv(tmp_path / "nope.tsv")

    def test_missing_column(self, tmp_path: Path) -> None:
        tsv = tmp_path / "bad.tsv"
        tsv.write_text("id\temail\n1\ta@test.com\n", encoding="utf-8")
        with pytest.raises(ValueError, match="missing columns"):
            load_tsv(tsv)

    def test_empty_email(self, tmp_path: Path) -> None:
        tsv = tmp_path / "bad.tsv"
        _write_tsv(
            tsv,
            [
                {
                    "id": "1",
                    "email": "",
                    "subject": "Hi",
                    "body": "Hello",
                    "status": "pending",
                }
            ],
        )
        with pytest.raises(ValueError, match="invalid email"):
            load_tsv(tsv)

    def test_empty_id(self, tmp_path: Path) -> None:
        tsv = tmp_path / "bad.tsv"
        _write_tsv(
            tsv,
            [
                {
                    "id": "",
                    "email": "a@test.com",
                    "subject": "Hi",
                    "body": "Hello",
                    "status": "pending",
                }
            ],
        )
        with pytest.raises(ValueError, match="id.*empty"):
            load_tsv(tsv)


class TestSaveTsv:
    def test_roundtrip(self, tmp_path: Path) -> None:
        tsv = tmp_path / "test.tsv"
        original = [
            {
                "id": "1",
                "email": "a@test.com",
                "subject": "S1",
                "body": "B1",
                "status": "pending",
            },
            {
                "id": "2",
                "email": "b@test.com",
                "subject": "S2",
                "body": "B2",
                "status": "sent",
            },
        ]
        _write_tsv(tsv, original)
        data = load_tsv(tsv)
        data[0]["status"] = "sent"
        save_tsv(tsv, data)
        reloaded = load_tsv(tsv)
        assert reloaded[0]["status"] == "sent"
        assert reloaded[1]["status"] == "sent"


class TestGetPending:
    def test_filters_pending(self) -> None:
        data = [
            {
                "id": "1",
                "email": "a@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            },
            {
                "id": "2",
                "email": "b@t.com",
                "subject": "",
                "body": "",
                "status": "sent",
            },
            {
                "id": "3",
                "email": "c@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            },
        ]
        pending = get_pending_emails(data)
        assert len(pending) == 2
        assert all(r["status"] == "pending" for r in pending)


class TestUpdateStatus:
    def test_updates_existing(self) -> None:
        data = [
            {
                "id": "1",
                "email": "a@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            }
        ]
        assert update_status(data, "1", "sent") is True
        assert data[0]["status"] == "sent"

    def test_missing_id(self) -> None:
        data = [
            {
                "id": "1",
                "email": "a@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            }
        ]
        assert update_status(data, "999", "sent") is False

    def test_invalid_status(self) -> None:
        data = [
            {
                "id": "1",
                "email": "a@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            }
        ]
        with pytest.raises(ValueError, match="Invalid status"):
            update_status(data, "1", "invalid")


class TestGetStats:
    def test_counts(self) -> None:
        data = [
            {
                "id": "1",
                "email": "a@t.com",
                "subject": "",
                "body": "",
                "status": "sent",
            },
            {
                "id": "2",
                "email": "b@t.com",
                "subject": "",
                "body": "",
                "status": "sent",
            },
            {
                "id": "3",
                "email": "c@t.com",
                "subject": "",
                "body": "",
                "status": "pending",
            },
            {
                "id": "4",
                "email": "d@t.com",
                "subject": "",
                "body": "",
                "status": "error",
            },
        ]
        stats = get_stats(data)
        assert stats["total"] == 4
        assert stats["sent"] == 2
        assert stats["pending"] == 1
        assert stats["error"] == 1
        assert len(stats["error_details"]) == 1
