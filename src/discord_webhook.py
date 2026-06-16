from __future__ import annotations

import requests

from src.config import Config


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    if minutes < 60:
        return f"{minutes}m {secs:.0f}s"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def send_stats_to_discord(
    config: Config, stats: dict[str, int | list], duration: float
) -> bool:
    if not config.discord_webhook_url:
        return False

    error_count = stats["error"]
    color = 0x2ECC71 if error_count == 0 else 0xE67E22

    embed = {
        "title": "📧 Bulk Email Send Report",
        "color": color,
        "fields": [
            {"name": "Total", "value": str(stats["total"]), "inline": True},
            {"name": "Sent", "value": str(stats["sent"]), "inline": True},
            {"name": "Failed", "value": str(stats["error"]), "inline": True},
            {"name": "Pending", "value": str(stats["pending"]), "inline": True},
            {"name": "Duration", "value": format_duration(duration), "inline": True},
        ],
    }

    if duration > 0 and stats["sent"] > 0:
        avg = duration / stats["sent"]
        embed["fields"].append(
            {"name": "Avg/Email", "value": f"{avg:.1f}s", "inline": True}
        )

    payload = {"embeds": [embed]}

    try:
        response = requests.post(config.discord_webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to send Discord notification: {e}")
        return False
