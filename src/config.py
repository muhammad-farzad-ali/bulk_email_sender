from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    discord_webhook_url: str | None


def load_config(env_file: str | None = None) -> Config:
    if env_file:
        env_path = Path(env_file)
    else:
        env_path = Path(".env")

    if not env_path.exists():
        print(f"Error: {env_path} not found.")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    load_dotenv(env_path)

    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL") or None

    missing = []
    if not smtp_host:
        missing.append("SMTP_HOST")
    if not smtp_user:
        missing.append("SMTP_USER")
    if not smtp_pass:
        missing.append("SMTP_PASS")

    if missing:
        print(f"Error: Missing required env vars: {', '.join(missing)}")
        print(f"Please set them in {env_path}")
        sys.exit(1)

    return Config(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_pass=smtp_pass,
        discord_webhook_url=discord_webhook_url,
    )


def validate_email_config(config: Config) -> tuple[bool, str]:
    if not config.smtp_host:
        return False, "SMTP_HOST is not set"
    if not config.smtp_user:
        return False, "SMTP_USER is not set"
    if not config.smtp_pass:
        return False, "SMTP_PASS is not set"
    if config.smtp_port not in (25, 465, 587, 2525):
        return (
            False,
            f"Unusual SMTP port: {config.smtp_port}. Expected 25, 465, 587, or 2525.",
        )
    return True, "OK"


def validate_discord_config(config: Config) -> tuple[bool, str]:
    if not config.discord_webhook_url:
        return False, "DISCORD_WEBHOOK_URL is not set (Discord notifications disabled)"
    if not config.discord_webhook_url.startswith("https://discord.com/api/webhooks/"):
        return (
            False,
            "DISCORD_WEBHOOK_URL does not look like a valid Discord webhook URL",
        )
    return True, "OK"
