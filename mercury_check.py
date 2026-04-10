"""
MercuryCI Planetary Status Module
Checks retrograde status and moon phase before allowing merges.
"""

import random
from datetime import date
from dataclasses import dataclass
from enum import Enum


# Multiple guidance messages per phase — one is picked at random each run.
PHASE_GUIDANCE: dict[str, list[str]] = {
    "New Moon": [
        "Fresh starts encouraged. Risky deploys discouraged.",
        "A blank slate. Good time to open that PR you've been sitting on.",
        "Plant seeds, not hotfixes. Intention matters right now.",
        "The void is full of possibility. Mostly bugs, but also possibility.",
    ],
    "Waxing Crescent": [
        "Good energy for new features.",
        "Momentum is building. Push the branch.",
        "Small steps. Commit often. The crescent rewards incrementalism.",
        "Something is beginning. Let it be a feature and not a fire.",
    ],
    "First Quarter": [
        "Build momentum. Ship incrementally.",
        "Half the light, all the energy. A good day to merge.",
        "Tension is productive right now. So is a thorough code review.",
        "Obstacles are clarifying. Debug with curiosity, not frustration.",
    ],
    "Waxing Gibbous": [
        "Refinement phase. Good for bug fixes.",
        "Almost full. Polish what you have before adding more.",
        "The code is close. Resist the urge to redesign everything.",
        "Good time for a second pass. Fresh eyes on old PRs.",
    ],
    "Full Moon": [
        "Emotions are high. Review carefully. Maybe hydrate.",
        "Peak energy. Ideal for big merges, but double-check your work.",
        "Everything feels urgent tonight. Most of it isn't. Breathe.",
        "The full moon illuminates what was hidden. So does `git diff`.",
        "High tides. High feelings. Low tolerance for flaky tests.",
    ],
    "Waning Gibbous": [
        "Integration and reflection. Good for docs.",
        "The sprint is winding down. Write the tests you skipped.",
        "Share what you've built. Demo it. Document it. Let it breathe.",
        "Gratitude phase. Thank your reviewers. Merge their feedback.",
    ],
    "Last Quarter": [
        "Release old patterns. Refactor with intention.",
        "What no longer serves the codebase can be deleted now.",
        "Good energy for technical debt. The kind you actually pay off.",
        "Let go of the branch you've been afraid to close.",
        "The stars say: delete the dead code. You know which code.",
    ],
    "Waning Crescent": [
        "Rest phase. Avoid major architecture decisions.",
        "The cycle is ending. Draft your PRs; don't merge them yet.",
        "Quiet time. Good for reading documentation you've been ignoring.",
        "The cosmos are resetting. So should your local environment.",
    ],
}

RETROGRADE_TOOLTIPS: list[str] = [
    "Not today, bestie. Mercury direct in {days} day{s}.",
    "Mercury is sorting through its feelings. Direct in {days} day{s}.",
    "The messenger planet is reconsidering. Back in {days} day{s}.",
    "Retrograde in progress. The merge can wait {days} day{s}.",
    "Even Mercury needs to reflect sometimes. Direct in {days} day{s}.",
    "Communications are spiritually delayed. Direct in {days} day{s}.",
]

CLEAR_TOOLTIPS: list[str] = [
    "{emoji} Merge available. {guidance}",
    "{emoji} Mercury is direct. {guidance}",
    "{emoji} The planets are aligned-ish. {guidance}",
    "{emoji} All systems nominal (cosmically speaking). {guidance}",
]


class MoonPhase(Enum):
    NEW_MOON       = ("🌑", "New Moon")
    WAXING_CRESCENT = ("🌒", "Waxing Crescent")
    FIRST_QUARTER  = ("🌓", "First Quarter")
    WAXING_GIBBOUS = ("🌔", "Waxing Gibbous")
    FULL_MOON      = ("🌕", "Full Moon")
    WANING_GIBBOUS = ("🌖", "Waning Gibbous")
    LAST_QUARTER   = ("🌗", "Last Quarter")
    WANING_CRESCENT = ("🌘", "Waning Crescent")

    def __init__(self, emoji, label):
        self.emoji = emoji
        self.label = label

    @property
    def guidance(self) -> str:
        return random.choice(PHASE_GUIDANCE[self.label])


# Known Mercury retrograde periods (extend as needed)
MERCURY_RETROGRADE_PERIODS = [
    (date(2026, 1, 10), date(2026, 1, 31)),
    (date(2026, 5, 5),  date(2026, 5, 28)),
    (date(2026, 9, 4),  date(2026, 9, 26)),
    (date(2025, 3, 15), date(2025, 4, 7)),
    (date(2025, 7, 18), date(2025, 8, 11)),
    (date(2025, 11, 9), date(2025, 11, 29)),
]


@dataclass
class CosmicStatus:
    moon_phase: MoonPhase
    mercury_retrograde: bool
    retrograde_ends: date | None
    check_date: date

    @property
    def merge_blocked(self) -> bool:
        return self.mercury_retrograde

    @property
    def days_until_direct(self) -> int | None:
        if self.retrograde_ends:
            return (self.retrograde_ends - self.check_date).days
        return None

    def merge_button_tooltip(self) -> str:
        if self.mercury_retrograde:
            days = self.days_until_direct
            s = 's' if days != 1 else ''
            template = random.choice(RETROGRADE_TOOLTIPS)
            return template.format(days=days, s=s)
        template = random.choice(CLEAR_TOOLTIPS)
        return template.format(emoji=self.moon_phase.emoji, guidance=self.moon_phase.guidance)

    def slack_header(self) -> str:
        phase = self.moon_phase
        if self.mercury_retrograde:
            days = self.days_until_direct
            status = random.choice([
                "RETROGRADE ACTIVE",
                f"Retrograde — direct in {days} day{'s' if days != 1 else ''}",
                "Mercury is in its feelings",
                "☿ retrograde",
            ])
        else:
            status = random.choice([
                "All planets nominal",
                "Mercury direct ✓",
                "Cosmically clear",
                "No retrogrades detected",
            ])
        return f"{phase.emoji} {phase.label} | Mercury: {status}"


def get_moon_phase(check_date: date | None = None) -> MoonPhase:
    """Calculate moon phase using a simplified lunar cycle model."""
    target = check_date or date.today()
    # Known new moon reference point
    known_new_moon = date(2000, 1, 6)
    days_since = (target - known_new_moon).days
    cycle_position = (days_since % 29.53) / 29.53

    thresholds = [
        (0.0625, MoonPhase.NEW_MOON),
        (0.1875, MoonPhase.WAXING_CRESCENT),
        (0.3125, MoonPhase.FIRST_QUARTER),
        (0.4375, MoonPhase.WAXING_GIBBOUS),
        (0.5625, MoonPhase.FULL_MOON),
        (0.6875, MoonPhase.WANING_GIBBOUS),
        (0.8125, MoonPhase.LAST_QUARTER),
        (0.9375, MoonPhase.WANING_CRESCENT),
        (1.0,    MoonPhase.NEW_MOON),
    ]

    for threshold, phase in thresholds:
        if cycle_position < threshold:
            return phase

    return MoonPhase.NEW_MOON


def is_mercury_retrograde(check_date: date | None = None) -> tuple[bool, date | None]:
    """Returns (is_retrograde, end_date)."""
    target = check_date or date.today()
    for start, end in MERCURY_RETROGRADE_PERIODS:
        if start <= target <= end:
            return True, end
    return False, None


def get_cosmic_status(check_date: date | None = None) -> CosmicStatus:
    target = check_date or date.today()
    moon = get_moon_phase(target)
    retrograde, end_date = is_mercury_retrograde(target)
    return CosmicStatus(
        moon_phase=moon,
        mercury_retrograde=retrograde,
        retrograde_ends=end_date,
        check_date=target,
    )


if __name__ == "__main__":
    status = get_cosmic_status()
    print(status.slack_header())
    print(f"Merge tooltip: {status.merge_button_tooltip()}")
