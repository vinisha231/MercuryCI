"""
MercuryCI Empathy Compiler
Wraps your build errors with the emotional support they deserve.
"""

import time
import random
from dataclasses import dataclass
from typing import Optional


EMPATHY_MESSAGES = {
    "NullPointerException": [
        "Hey, I know this is hard.\nYou have a null pointer exception on line {line}.\nYou're doing great.",
        "Something was expected to be there, and it wasn't.\nLine {line}. We've all been there.",
    ],
    "SegmentationFault": [
        "Segmentation fault.\nMercury is also in retrograde right now, so honestly? Same.",
        "The memory is confused. The cosmos are confused.\nYou are not alone in this.",
    ],
    "UnusedCode": [
        "This function hasn't been used in 3 years.\nYou don't have to hold onto things forever.",
        "Dead code detected. Sometimes we keep things around\nbecause letting go is hard. It's okay to delete it.",
    ],
    "SyntaxError": [
        "A small thing out of place.\nLine {line}. Even the best writers need editors.",
        "Syntax error on line {line}.\nThe intention was clear. The syntax just needs a little love.",
    ],
    "TimeoutError": [
        "This took longer than expected.\nSome things need more time. That's not a failure — it's information.",
        "Build timed out.\nMercury may be moving slowly right now too. You're in good company.",
    ],
    "DependencyConflict": [
        "Two things that both want to be in charge.\nLine {line}. A relatable situation.",
        "Dependency conflict detected.\nNot everything is compatible, and that's okay. Some things aren't meant to merge.",
    ],
    "default": [
        "Something went wrong on line {line}.\nYou noticed. You're looking at it. That's already the hard part.",
        "An error occurred.\nEvery bug found is a bug that can be fixed. You've got this.",
    ],
}

RETROGRADE_SUFFIX = "\n\n  (Mercury is in retrograde. The compiler feels this deeply.)"


@dataclass
class EmpathyError:
    error_type: str
    line: Optional[int]
    raw_message: str
    mercury_retrograde: bool = False
    empathy_level: str = "high"

    def pause_duration(self) -> float:
        levels = {"low": 1.0, "medium": 2.0, "high": 3.0, "scorpio": 5.0}
        return levels.get(self.empathy_level, 3.0)

    def format(self) -> str:
        templates = EMPATHY_MESSAGES.get(self.error_type, EMPATHY_MESSAGES["default"])
        message = random.choice(templates).format(line=self.line or "?")

        if self.mercury_retrograde:
            message += RETROGRADE_SUFFIX

        return message


def compile_with_empathy(errors: list[EmpathyError]) -> None:
    """Process build errors through the Empathy Compiler."""

    if not errors:
        print("\n  Build passed. The code is well. Take a moment to appreciate that.\n")
        return

    print(f"\n  MercuryCI found {len(errors)} thing(s) to work through together.\n")

    for i, error in enumerate(errors, 1):
        print(f"  [{i}/{len(errors)}] Gathering itself", end="", flush=True)

        for _ in range(3):
            time.sleep(error.pause_duration() / 3)
            print(".", end="", flush=True)

        print("\n")
        print("  " + "\n  ".join(error.format().splitlines()))
        print()
        time.sleep(0.5)

    print("  The compiler believes in you. Please address the above when you're ready.\n")
