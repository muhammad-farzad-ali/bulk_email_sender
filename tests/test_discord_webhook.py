from unittest.mock import MagicMock, patch

from src.config import Config
from src.discord_webhook import format_duration, send_stats_to_discord


def _make_config(
    webhook_url: str | None = "https://discord.com/api/webhooks/test",
) -> Config:
    return Config(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="user@test.com",
        smtp_pass="pass123",
        discord_webhook_url=webhook_url,
    )


class TestFormatDuration:
    def test_seconds(self) -> None:
        assert format_duration(30.5) == "30.5s"

    def test_minutes(self) -> None:
        assert format_duration(125.0) == "2m 5s"

    def test_hours(self) -> None:
        assert format_duration(3665.0) == "1h 1m"


class TestSendStats:
    @patch("src.discord_webhook.requests.post")
    def test_success(self, mock_post: MagicMock) -> None:
        mock_post.return_value.raise_for_status = MagicMock()
        config = _make_config()
        stats = {"total": 10, "sent": 8, "error": 2, "pending": 0, "error_details": []}
        result = send_stats_to_discord(config, stats, 60.0)
        assert result is True
        mock_post.assert_called_once()

    @patch("src.discord_webhook.requests.post")
    def test_http_error(self, mock_post: MagicMock) -> None:
        import requests

        mock_post.side_effect = requests.exceptions.RequestException("fail")
        config = _make_config()
        stats = {"total": 10, "sent": 8, "error": 2, "pending": 0, "error_details": []}
        result = send_stats_to_discord(config, stats, 60.0)
        assert result is False

    def test_no_webhook(self) -> None:
        config = _make_config(webhook_url=None)
        stats = {"total": 10, "sent": 8, "error": 2, "pending": 0, "error_details": []}
        result = send_stats_to_discord(config, stats, 60.0)
        assert result is False
