"""
MercuryCI Birth Chart Parser
Reads astrological data from GitHub profile bios, saved config, or user prompt.

Expected bio format:
  ☀️ Scorpio | 🌙 Cancer | ⬆️ Virgo
  or any reasonable variation thereof.
"""

import re
from dataclasses import dataclass


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

# (month, day) ranges — end date is inclusive
BIRTHDATE_TO_SIGN = [
    ((3, 21), (4, 19),   "Aries"),
    ((4, 20), (5, 20),   "Taurus"),
    ((5, 21), (6, 20),   "Gemini"),
    ((6, 21), (7, 22),   "Cancer"),
    ((7, 23), (8, 22),   "Leo"),
    ((8, 23), (9, 22),   "Virgo"),
    ((9, 23), (10, 22),  "Libra"),
    ((10, 23), (11, 21), "Scorpio"),
    ((11, 22), (12, 21), "Sagittarius"),
    ((12, 22), (12, 31), "Capricorn"),
    ((1, 1),  (1, 19),   "Capricorn"),
    ((1, 20), (2, 18),   "Aquarius"),
    ((2, 19), (3, 20),   "Pisces"),
]


def birthdate_to_sign(month: int, day: int) -> str:
    """Converts a birth month and day to a sun sign."""
    for (start_m, start_d), (end_m, end_d), sign in BIRTHDATE_TO_SIGN:
        in_range = (
            (month == start_m and day >= start_d) or
            (month == end_m and day <= end_d) or
            (start_m < month < end_m)
        )
        if in_range:
            return sign
    return FALLBACK_SIGN


def prompt_for_sign(username: str) -> "BirthChart":
    """
    Interactively prompts the user to enter their sign or birth date.
    Saves the result to config so they're never asked again.
    """
    from config import save_user_profile, UserProfile

    print(f"\n  MercuryCI couldn't find a zodiac sign for @{username}.")
    print("  The pipeline needs this to function at full cosmic capacity.\n")
    print("  How would you like to provide it?")
    print("  1. Enter my sun sign directly")
    print("  2. Enter my birth month and day")
    print("  3. Skip for now (defaults to Libra)\n")

    choice = input("  Choice: ").strip()

    if choice == "1":
        print(f"\n  Signs: {', '.join(ZODIAC_SIGNS)}")
        raw = input("  Sun sign: ").strip().capitalize()
        if raw in ZODIAC_SIGNS:
            profile = UserProfile(sun_sign=raw, source="manual")
            save_user_profile(username, profile)
            print(f"\n  Got it. @{username} is a {raw}. Saved to ~/.mercuryci/config.json")
            print("  To change this later, run: python settings.py\n")
            return BirthChart(sun_sign=raw)
        else:
            print(f"  '{raw}' isn't recognised. Defaulting to Libra.\n")
            return BirthChart()

    elif choice == "2":
        try:
            month = int(input("  Birth month (1-12): ").strip())
            day   = int(input("  Birth day (1-31):   ").strip())
            sign  = birthdate_to_sign(month, day)
            profile = UserProfile(sun_sign=sign, source="birthdate")
            save_user_profile(username, profile)
            print(f"\n  {month}/{day} → {sign}. Saved to ~/.mercuryci/config.json")
            print("  To change this later, run: python settings.py\n")
            return BirthChart(sun_sign=sign)
        except ValueError:
            print("  Couldn't parse that. Defaulting to Libra.\n")
            return BirthChart()

    else:
        print("  Defaulting to Libra. Run `python settings.py` whenever you're ready.\n")
        return BirthChart()


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


def fetch_chart_from_github(
    username: str,
    github_token: str | None = None,
    interactive: bool = False,
) -> BirthChart:
    """
    Resolves a birth chart for a GitHub user using this priority order:
      1. Saved config (~/.mercuryci/config.json)
      2. GitHub profile bio
      3. Interactive prompt (if interactive=True), otherwise defaults to Libra
    """
    from config import get_user_profile, UserProfile

    # 1. Check saved config
    saved = get_user_profile(username)
    if saved:
        return BirthChart(
            sun_sign=saved.sun_sign,
            moon_sign=saved.moon_sign,
            rising_sign=saved.rising_sign,
        )

    # 2. Try GitHub bio
    bio = ""
    try:
        import urllib.request, json
        url = f"https://api.github.com/users/{username}"
        headers = {"User-Agent": "MercuryCI/1.0"}
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            bio = json.loads(resp.read()).get("bio") or ""
    except Exception as e:
        print(f"  [MercuryCI] Could not reach GitHub API for @{username}: {e}")

    if bio:
        chart = parse_birth_chart_from_bio(bio)
        if chart.sun_sign != FALLBACK_SIGN:
            return chart

    # 3. Prompt or fall back
    if interactive:
        return prompt_for_sign(username)

    print(f"  [MercuryCI] No sign found for @{username}. Defaulting to Libra.")
    print(f"  Run `python settings.py --user {username}` to set your sign.\n")
    return BirthChart()
