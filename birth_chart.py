"""
MercuryCI Birth Chart Parser
Reads astrological data from GitHub profile bios.

Expected bio format:
  ☀️ Scorpio | 🌙 Cancer | ⬆️ Virgo
  or any reasonable variation thereof.
"""

import re
from dataclasses import dataclass, field


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

SIGN_COMPATIBILITY = {
    "Fire":  {"Fire": 0.9, "Air": 0.8, "Earth": 0.5, "Water": 0.4},
    "Earth": {"Earth": 0.9, "Water": 0.8, "Fire": 0.5, "Air": 0.4},
    "Air":   {"Air": 0.9, "Fire": 0.8, "Water": 0.5, "Earth": 0.4},
    "Water": {"Water": 0.9, "Earth": 0.8, "Air": 0.5, "Fire": 0.4},
}

FALLBACK_SIGN = "Libra"  # Most balanced, best default


@dataclass
class BirthChart:
    sun_sign: str = FALLBACK_SIGN
    moon_sign: str | None = None
    rising_sign: str | None = None
    raw_bio: str = ""

    @property
    def primary_element(self) -> str:
        return SIGN_ELEMENTS.get(self.sun_sign, "Air")

    def reviewer_compatibility(self, other: "BirthChart") -> float:
        """
        Returns a compatibility score (0.0 - 1.0) between two contributors.
        Used to weight code review assignment. Obviously.
        """
        my_element = self.primary_element
        their_element = other.primary_element
        return SIGN_COMPATIBILITY.get(my_element, {}).get(their_element, 0.5)

    def pipeline_temperament(self) -> str:
        """Returns a description of how this chart affects pipeline behavior."""
        temperaments = {
            "Aries": "Fast builds, impatient with long test suites. May skip lint.",
            "Taurus": "Stable, reliable. Resistant to dependency upgrades.",
            "Gemini": "Inconsistent test results. Excellent PR descriptions.",
            "Cancer": "Sensitive to flaky tests. Clings to deprecated APIs.",
            "Leo": "Dramatic error messages. Excellent changelog entries.",
            "Virgo": "Perfect formatting. Will open a PR to fix your PR.",
            "Libra": "Balanced and fair. Takes forever to decide on a merge strategy.",
            "Scorpio": "Deep dives into root causes. Holds grudges against bad commits.",
            "Sagittarius": "Ships fast, breaks things. Optimistic about hotfixes.",
            "Capricorn": "Structured, methodical. Never merges without full test coverage.",
            "Aquarius": "Experimental architecture. Half the deps are unpublished.",
            "Pisces": "Intuitive debugging. Comments are mostly vibes.",
        }
        return temperaments.get(self.sun_sign, "Unknown temperament. Check your bio.")

    def __str__(self) -> str:
        parts = [f"Sun: {self.sun_sign}"]
        if self.moon_sign:
            parts.append(f"Moon: {self.moon_sign}")
        if self.rising_sign:
            parts.append(f"Rising: {self.rising_sign}")
        return " | ".join(parts)


def parse_birth_chart_from_bio(bio: str) -> BirthChart:
    """
    Parses a GitHub bio string for astrological signs.

    Supported formats:
      ☀️ Scorpio | 🌙 Cancer | ⬆️ Virgo
      Sun: Scorpio, Moon: Cancer, Rising: Virgo
      scorpio sun, cancer moon, virgo rising
    """
    if not bio:
        return BirthChart(raw_bio=bio)

    signs_pattern = "|".join(ZODIAC_SIGNS)

    sun_match = re.search(
        rf"(?:☀️?|sun[:\s]+)[\s]*({signs_pattern})",
        bio, re.IGNORECASE
    )
    moon_match = re.search(
        rf"(?:🌙|moon[:\s]+)[\s]*({signs_pattern})",
        bio, re.IGNORECASE
    )
    rising_match = re.search(
        rf"(?:⬆️?|rising[:\s]+|asc(?:endant)?[:\s]+)[\s]*({signs_pattern})",
        bio, re.IGNORECASE
    )

    # Fallback: just grab any zodiac sign mentioned first
    any_sign = re.search(rf"\b({signs_pattern})\b", bio, re.IGNORECASE)

    sun = (sun_match.group(1).capitalize() if sun_match
           else any_sign.group(1).capitalize() if any_sign
           else FALLBACK_SIGN)

    return BirthChart(
        sun_sign=sun,
        moon_sign=moon_match.group(1).capitalize() if moon_match else None,
        rising_sign=rising_match.group(1).capitalize() if rising_match else None,
        raw_bio=bio,
    )


def fetch_chart_from_github(username: str, github_token: str | None = None) -> BirthChart:
    """
    Fetches a GitHub user's bio and parses their birth chart from it.
    Requires the GitHub API. Fails gracefully to Libra.
    """
    try:
        import urllib.request, json
        url = f"https://api.github.com/users/{username}"
        headers = {"User-Agent": "MercuryCI/1.0"}
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            bio = data.get("bio") or ""
            chart = parse_birth_chart_from_bio(bio)
            if chart.sun_sign == FALLBACK_SIGN and not bio:
                print(f"  [MercuryCI] No birth chart found in @{username}'s bio. Defaulting to Libra rising.")
            return chart
    except Exception as e:
        print(f"  [MercuryCI] Could not fetch chart for @{username}: {e}. Defaulting to Libra.")
        return BirthChart()
