"""
MercuryCI Settings
Interactive menu to view and change your astrological profile.

Usage:
  python settings.py
  python settings.py --user <github_username>
"""

import argparse
import sys
from config import get_user_profile, save_user_profile, delete_user_profile, UserProfile
from birth_chart import ZODIAC_SIGNS, birthdate_to_sign, prompt_for_sign


MENU = """
  MercuryCI Settings
  ──────────────────
  1. View my profile
  2. Set sign manually
  3. Set sign by birth date
  4. Clear saved profile
  5. Exit
"""


def view_profile(username: str) -> None:
    profile = get_user_profile(username)
    if not profile:
        print(f"\n  No saved profile for @{username}.")
        print("  Sign will be read from your GitHub bio, or you'll be prompted on first run.\n")
        return

    print(f"\n  Profile for @{username}:")
    print(f"  Sun sign:    {profile.sun_sign}")
    if profile.moon_sign:
        print(f"  Moon sign:   {profile.moon_sign}")
    if profile.rising_sign:
        print(f"  Rising sign: {profile.rising_sign}")
    print(f"  Source:      {profile.source}\n")


def set_sign_manually(username: str) -> None:
    print("\n  Enter your sun sign (or leave blank to cancel):")
    print("  " + ", ".join(ZODIAC_SIGNS))
    sun = input("\n  Sun sign: ").strip().capitalize()
    if not sun:
        print("  Cancelled.\n")
        return
    if sun not in ZODIAC_SIGNS:
        print(f"  '{sun}' isn't a recognised sign. Check spelling and try again.\n")
        return

    moon = input("  Moon sign (optional, press Enter to skip): ").strip().capitalize() or None
    if moon and moon not in ZODIAC_SIGNS:
        print(f"  '{moon}' isn't recognised — skipping moon sign.\n")
        moon = None

    rising = input("  Rising sign (optional, press Enter to skip): ").strip().capitalize() or None
    if rising and rising not in ZODIAC_SIGNS:
        print(f"  '{rising}' isn't recognised — skipping rising sign.\n")
        rising = None

    profile = UserProfile(sun_sign=sun, moon_sign=moon, rising_sign=rising, source="manual")
    save_user_profile(username, profile)
    print(f"\n  Saved. @{username} is a {sun}. The pipeline will act accordingly.\n")


def set_sign_by_birthdate(username: str) -> None:
    print("\n  Enter your birth month and day:")
    try:
        month = int(input("  Month (1-12): ").strip())
        day = int(input("  Day (1-31): ").strip())
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError
    except ValueError:
        print("  Invalid date. Please enter numbers only.\n")
        return

    sign = birthdate_to_sign(month, day)
    profile = UserProfile(sun_sign=sign, source="birthdate")
    save_user_profile(username, profile)
    print(f"\n  {month}/{day} → {sign}. Profile saved for @{username}.\n")


def clear_profile(username: str) -> None:
    confirm = input(f"\n  Clear saved profile for @{username}? (y/n): ").strip().lower()
    if confirm == "y":
        deleted = delete_user_profile(username)
        if deleted:
            print(f"  Profile cleared. @{username} will be prompted again on next run.\n")
        else:
            print(f"  No profile found for @{username}.\n")
    else:
        print("  Cancelled.\n")


def run_menu(username: str) -> None:
    print(f"\n  Logged in as @{username}")
    while True:
        print(MENU)
        choice = input("  Choice: ").strip()
        if choice == "1":
            view_profile(username)
        elif choice == "2":
            set_sign_manually(username)
        elif choice == "3":
            set_sign_by_birthdate(username)
        elif choice == "4":
            clear_profile(username)
        elif choice == "5":
            print("  The stars will remember your settings.\n")
            break
        else:
            print("  Please enter 1–5.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="MercuryCI Settings")
    parser.add_argument("--user", default=None, help="GitHub username (defaults to current git user)")
    args = parser.parse_args()

    if args.user:
        username = args.user
    else:
        import subprocess
        result = subprocess.run(["gh", "api", "user", "-q", ".login"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            username = result.stdout.strip()
        else:
            username = input("  GitHub username: ").strip()
            if not username:
                print("  No username provided. Exiting.\n")
                sys.exit(1)

    run_menu(username)


if __name__ == "__main__":
    main()
