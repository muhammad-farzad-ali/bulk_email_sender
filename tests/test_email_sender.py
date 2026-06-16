from unittest.mock import MagicMock, patch

from src.config import Config
from src.email_sender import send_email, check_connection


def _make_config() -> Config:
    return Config(
        smtp_host="smtp.test.com",
        smtp_port=587,
        smtp_user="user@test.com",
        smtp_pass="pass123",
        discord_webhook_url=None,
    )


class TestSendEmail:
    @patch("src.email_sender.smtplib.SMTP")
    def test_success(self, MockSMTP: MagicMock) -> None:
        server = MockSMTP.return_value.__enter__.return_value
        config = _make_config()
        ok, err = send_email(config, "bob@test.com", "Subject", "Body")
        assert ok is True
        assert err == ""
        server.login.assert_called_once_with("user@test.com", "pass123")
        server.sendmail.assert_called_once()

    @patch("src.email_sender.smtplib.SMTP")
    def test_auth_failure(self, MockSMTP: MagicMock) -> None:
        import smtplib

        server = MockSMTP.return_value.__enter__.return_value
        server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        config = _make_config()
        ok, err = send_email(config, "bob@test.com", "Subject", "Body")
        assert ok is False
        assert "authentication failed" in err.lower()

    @patch("src.email_sender.smtplib.SMTP")
    def test_connection_refused(self, MockSMTP: MagicMock) -> None:
        MockSMTP.return_value.__enter__.side_effect = ConnectionRefusedError
        config = _make_config()
        ok, err = send_email(config, "bob@test.com", "Subject", "Body")
        assert ok is False
        assert "refused" in err.lower()


class TestConnection:
    @patch("src.email_sender.smtplib.SMTP")
    def test_success(self, MockSMTP: MagicMock) -> None:
        config = _make_config()
        ok, msg = check_connection(config)
        assert ok is True
        assert "successful" in msg.lower()

    @patch("src.email_sender.smtplib.SMTP")
    def test_auth_failure(self, MockSMTP: MagicMock) -> None:
        import smtplib

        server = MockSMTP.return_value.__enter__.return_value
        server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        config = _make_config()
        ok, msg = check_connection(config)
        assert ok is False
        assert "authentication failed" in msg.lower()
