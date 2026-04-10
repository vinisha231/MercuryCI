"""
MercuryCI Slack Notifier
Posts cosmically-aware CI updates to #engineering.
"""

import json
import urllib.request
from dataclasses import dataclass
from typing import Optional

from mercury_check import CosmicStatus, MoonPhase
from birth_chart import BirthChart


HEALING_MESSAGES = [
    "Sending healing. 🌿",
    "The stars are watching over this PR. 🌟",
    "Rest. The cosmos will sort this out. 🪐",
    "Mercury will be direct soon. Until then, be gentle with yourself. 💫",
    "This PR has good bones. It needs time. 🌱",
    "Not every door opens on the first push. 🌙",
]

MERGE_SUCCESS_MESSAGES = [
    "The pipeline is pleased. The cosmos are aligned. Ship it. ✨",
    "Mercury is direct. The moon is favorable. Go forth. 🚀",
    "Build passed. The stars have spoken. 🌟",
    "All checks green. All planets nominal. 🪐",
]


@dataclass
class PREvent:
    pr_number: int
    pr_title: str
    author: str
    repo: str
    url: str
    birth_chart: Optional[BirthChart] = None
    build_passed: bool = True
    error_summary: Optional[str] = None


def _healing_message(status: CosmicStatus) -> str:
    import random
    base = random.choice(HEALING_MESSAGES)
    if status.moon_phase == MoonPhase.FULL_MOON:
        base += " (Full moon energy is intense tonight — be extra kind to yourself.)"
    return base


def format_blocked_message(pr: PREvent, status: CosmicStatus) -> dict:
    days = status.days_until_direct or "?"
    author_display = pr.birth_chart.sun_sign if pr.birth_chart else "Unknown sign"

    text = (
        f"{status.moon_phase.emoji} *MercuryCI Alert:* {pr.author}'s PR #{pr.pr_number} is blocked.\n"
        f"Mercury retrograde ends in *{days} day{'s' if days != 1 else ''}*.\n"
    )

    if pr.error_summary:
        text += f"The compiler says the code \"{pr.error_summary}\"\n"

    text += _healing_message(status)

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": status.slack_header()},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "View PR"},
                    "url": pr.url,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f"Author birth chart: {pr.birth_chart or 'not found (defaulting to Libra)'} | "
                            f"{status.moon_phase.guidance}"
                        ),
                    }
                ],
            },
        ]
    }


def format_success_message(pr: PREvent, status: CosmicStatus) -> dict:
    import random
    text = (
        f"*{random.choice(MERGE_SUCCESS_MESSAGES)}*\n"
        f"PR #{pr.pr_number} — _{pr.pr_title}_ — is clear to merge.\n"
        f"{status.moon_phase.emoji} {status.moon_phase.guidance}"
    )

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": status.slack_header()},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Merge PR"},
                    "url": pr.url,
                    "style": "primary",
                },
            },
        ]
    }


def post_to_slack(webhook_url: str, payload: dict) -> bool:
    """Posts a message payload to a Slack webhook. Returns True on success."""
    try:
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            webhook_url,
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[MercuryCI] Slack notification failed: {e}")
        return False


def notify(webhook_url: str, pr: PREvent, status: CosmicStatus) -> bool:
    if status.merge_blocked:
        payload = format_blocked_message(pr, status)
    else:
        payload = format_success_message(pr, status)
    return post_to_slack(webhook_url, payload)
