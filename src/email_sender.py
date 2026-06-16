from __future__ import annotations

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config import Config


def send_email(
    config: Config, to_email: str, subject: str, body: str
) -> tuple[bool, str]:
    msg = MIMEMultipart()
    msg["From"] = config.smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

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


def test_connection(config: Config) -> tuple[bool, str]:
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
