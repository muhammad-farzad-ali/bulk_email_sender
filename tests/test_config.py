import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import (
    Config,
    load_config,
    validate_discord_config,
    validate_email_config,
)


class TestLoadConfig:
    def test_loads_from_env(self, tmp_path: Path) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text(
            "SMTP_HOST=smtp.test.com\n"
            "SMTP_PORT=465\n"
            "SMTP_USER=user@test.com\n"
            "SMTP_PASS=secret\n"
            "DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/test\n",
            encoding="utf-8",
        )
        config = load_config(str(env_file))
        assert config.smtp_host == "smtp.test.com"
        assert config.smtp_port == 465
        assert config.smtp_user == "user@test.com"
        assert config.smtp_pass == "secret"
        assert config.discord_webhook_url == "https://discord.com/api/webhooks/test"

    def test_missing_file_exits(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            load_config(str(tmp_path / "nope.env"))

    def test_missing_required_var(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        env_file = tmp_path / ".env"
        env_file.write_text("SMTP_HOST=smtp.test.com\n", encoding="utf-8")
        monkeypatch.delenv("SMTP_USER", raising=False)
        monkeypatch.delenv("SMTP_PASS", raising=False)
        with pytest.raises(SystemExit):
            load_config(str(env_file))


class TestValidateEmail:
    def test_valid(self) -> None:
        config = Config("smtp.test.com", 587, "u", "p", None)
        ok, _ = validate_email_config(config)
        assert ok is True

    def test_missing_host(self) -> None:
        config = Config("", 587, "u", "p", None)
        ok, _ = validate_email_config(config)
        assert ok is False


class TestValidateDiscord:
    def test_valid(self) -> None:
        config = Config("h", 587, "u", "p", "https://discord.com/api/webhooks/test")
        ok, _ = validate_discord_config(config)
        assert ok is True

    def test_no_url(self) -> None:
        config = Config("h", 587, "u", "p", None)
        ok, _ = validate_discord_config(config)
        assert ok is False

    def test_bad_url(self) -> None:
        config = Config("h", 587, "u", "p", "https://evil.com/hook")
        ok, _ = validate_discord_config(config)
        assert ok is False
