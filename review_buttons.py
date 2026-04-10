"""
MercuryCI Review Buttons
Injects custom approval options into the PR review flow.

Extends GitHub's standard review API with three sacred choices:
  - LGTM (classic)
  - The vibes are right
  - I defer to the cosmos
"""

import random
from dataclasses import dataclass
from enum import Enum
from datetime import date

from mercury_check import get_cosmic_status, MoonPhase


class ReviewDecision(Enum):
    LGTM = "LGTM"
    VIBES_ARE_RIGHT = "VIBES_ARE_RIGHT"
    DEFER_TO_COSMOS = "DEFER_TO_COSMOS"


REVIEW_BUTTONS = [
    {
        "id": ReviewDecision.LGTM,
        "label": "✅ LGTM",
        "description": "Looks good to me. I read the code.",
        "github_state": "APPROVED",
    },
    {
        "id": ReviewDecision.VIBES_ARE_RIGHT,
        "label": "🌙 The vibes are right",
        "description": "Energetically aligned. The code feels correct.",
        "github_state": "APPROVED",
    },
    {
        "id": ReviewDecision.DEFER_TO_COSMOS,
        "label": "🪐 I defer to the cosmos",
        "description": "I read the code. The stars must decide.",
        "github_state": None,  # resolved at runtime
    },
]


@dataclass
class ReviewOutcome:
    decision: ReviewDecision
    reviewer: str
    github_state: str  # "APPROVED" or "REQUEST_CHANGES"
    cosmic_note: str | None = None


def _cosmos_decides(check_date: date | None = None) -> tuple[str, str]:
    """
    The cosmos makes the review decision.

    Weighting:
    - Full moon: 70% approve (emotions are high but energy is peak)
    - New moon: 50/50 (void, uncertain)
    - Waning phases: 40% approve (release energy)
    - Waxing phases: 60% approve (building energy)
    """
    status = get_cosmic_status(check_date)
    phase = status.moon_phase

    weights = {
        MoonPhase.FULL_MOON:        0.70,
        MoonPhase.WAXING_GIBBOUS:   0.65,
        MoonPhase.FIRST_QUARTER:    0.60,
        MoonPhase.WAXING_CRESCENT:  0.60,
        MoonPhase.NEW_MOON:         0.50,
        MoonPhase.WANING_GIBBOUS:   0.45,
        MoonPhase.LAST_QUARTER:     0.40,
        MoonPhase.WANING_CRESCENT:  0.40,
    }

    if status.mercury_retrograde:
        # Retrograde applies a -15% penalty to approval chances
        base_weight = weights.get(phase, 0.5) - 0.15
    else:
        base_weight = weights.get(phase, 0.5)

    approved = random.random() < base_weight
    state = "APPROVED" if approved else "REQUEST_CHANGES"

    note = (
        f"The cosmos ({phase.emoji} {phase.label}"
        f"{', Mercury retrograde' if status.mercury_retrograde else ''}) "
        f"{'favor' if approved else 'do not favor'} this merge."
    )

    return state, note


def process_review(
    decision: ReviewDecision,
    reviewer: str,
    check_date: date | None = None,
) -> ReviewOutcome:
    """
    Resolves a review button click into a GitHub review state.
    """
    if decision == ReviewDecision.DEFER_TO_COSMOS:
        state, note = _cosmos_decides(check_date)
        return ReviewOutcome(
            decision=decision,
            reviewer=reviewer,
            github_state=state,
            cosmic_note=note,
        )

    button = next(b for b in REVIEW_BUTTONS if b["id"] == decision)
    return ReviewOutcome(
        decision=decision,
        reviewer=reviewer,
        github_state=button["github_state"],
        cosmic_note=None,
    )


def render_review_ui(mercury_retrograde: bool = False) -> str:
    """Returns a text representation of the review button UI."""
    lines = ["\n  Choose your review:\n"]
    for button in REVIEW_BUTTONS:
        disabled = (
            button["id"] != ReviewDecision.DEFER_TO_COSMOS and mercury_retrograde
            and button["id"] == ReviewDecision.LGTM
        )
        suffix = "  [cosmos pending]" if button["id"] == ReviewDecision.DEFER_TO_COSMOS else ""
        lines.append(f"  {button['label']}{suffix}")
        lines.append(f"    {button['description']}")
    return "\n".join(lines)
