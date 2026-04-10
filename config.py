"""
MercuryCI Config
Stores user astrological profiles locally at ~/.mercuryci/config.json
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


CONFIG_DIR = Path.home() / ".mercuryci"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class UserProfile:
    sun_sign: str
    moon_sign: Optional[str] = None
    rising_sign: Optional[str] = None
    source: str = "manual"  # "bio", "manual", "birthdate"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_user_profile(username: str) -> Optional[UserProfile]:
    config = load_config()
    users = config.get("users", {})
    data = users.get(username)
    if not data:
        return None
    return UserProfile(
        sun_sign=data["sun_sign"],
        moon_sign=data.get("moon_sign"),
        rising_sign=data.get("rising_sign"),
        source=data.get("source", "manual"),
    )


def save_user_profile(username: str, profile: UserProfile) -> None:
    config = load_config()
    if "users" not in config:
        config["users"] = {}
    config["users"][username] = asdict(profile)
    save_config(config)


def delete_user_profile(username: str) -> bool:
    config = load_config()
    users = config.get("users", {})
    if username in users:
        del users[username]
        config["users"] = users
        save_config(config)
        return True
    return False
