from __future__ import annotations

import re
import smtplib
import ssl
from html import unescape
from html.parser import HTMLParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import Config


class _HTMLToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._block_tags = {
            "p",
            "div",
            "br",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "tr",
            "blockquote",
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._block_tags:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        text = unescape(text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text.strip()


def html_to_text(html: str) -> str:
    parser = _HTMLToText()
    parser.feed(html)
    return parser.get_text()


def send_email(
    config: Config, to_email: str, subject: str, body: str
) -> tuple[bool, str]:
    plain_body = html_to_text(body) if "<" in body else body
    msg = MIMEMultipart()
    msg["From"] = config.smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(plain_body, "plain"))

    try:
        if config.smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                config.smtp_host, config.smtp_port, context=context
            ) as server:
                server.login(config.smtp_user, config.smtp_pass)
                server.sendmail(config.smtp_user, to_email, msg.as_string())
        else:
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                server.ehlo()
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
                server.login(config.smtp_user, config.smtp_pass)
                server.sendmail(config.smtp_user, to_email, msg.as_string())

        return True, ""

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed - check username/password"
    except smtplib.SMTPRecipientsRefused:
        return False, f"Recipient refused: {to_email}"
    except ConnectionRefusedError:
        return False, f"Connection refused by {config.smtp_host}:{config.smtp_port}"
    except TimeoutError:
        return False, f"Connection to {config.smtp_host}:{config.smtp_port} timed out"
    except OSError as e:
        return False, f"Network error: {e}"


def check_connection(config: Config) -> tuple[bool, str]:
    try:
        if config.smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                config.smtp_host, config.smtp_port, context=context
            ) as server:
                server.login(config.smtp_user, config.smtp_pass)
        else:
            with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
                server.ehlo()
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
                server.login(config.smtp_user, config.smtp_pass)

        return True, "Connection successful"

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed - check username/password"
    except ConnectionRefusedError:
        return False, f"Connection refused by {config.smtp_host}:{config.smtp_port}"
    except TimeoutError:
        return False, f"Connection to {config.smtp_host}:{config.smtp_port} timed out"
    except OSError as e:
        return False, f"Network error: {e}"
