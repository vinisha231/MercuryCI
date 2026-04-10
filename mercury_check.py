"""
MercuryCI Planetary Status Module
Checks retrograde status and moon phase before allowing merges.
"""

import math
from datetime import date, datetime
from dataclasses import dataclass
from enum import Enum


class MoonPhase(Enum):
    NEW_MOON = ("🌑", "New Moon", "Fresh starts encouraged. Risky deploys discouraged.")
    WAXING_CRESCENT = ("🌒", "Waxing Crescent", "Good energy for new features.")
    FIRST_QUARTER = ("🌓", "First Quarter", "Build momentum. Ship incrementally.")
    WAXING_GIBBOUS = ("🌔", "Waxing Gibbous", "Refinement phase. Good for bug fixes.")
    FULL_MOON = ("🌕", "Full Moon", "Emotions are high. Review carefully. Maybe hydrate.")
    WANING_GIBBOUS = ("🌖", "Waning Gibbous", "Integration and reflection. Good for docs.")
    LAST_QUARTER = ("🌗", "Last Quarter", "Release old patterns. Refactor with intention.")
    WANING_CRESCENT = ("🌘", "Waning Crescent", "Rest phase. Avoid major architecture decisions.")

    def __init__(self, emoji, label, guidance):
        self.emoji = emoji
        self.label = label
        self.guidance = guidance


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
            return f"Not today, bestie. Mercury direct in {days} day{'s' if days != 1 else ''}."
        return f"{self.moon_phase.emoji} Merge available. {self.moon_phase.guidance}"

    def slack_header(self) -> str:
        phase = self.moon_phase
        status = "RETROGRADE ACTIVE" if self.mercury_retrograde else "All planets nominal"
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
