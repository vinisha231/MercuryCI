# MercuryCI 🪐
### The Emotionally Aware, Astrologically Governed CI/CD Pipeline

> *"Your code deserves to be seen. Your feelings deserve to be validated. Your merge deserves to wait until Mercury is direct."*

---

## What is MercuryCI?

MercuryCI is the CI/CD pipeline that finally acknowledges that software engineering is a deeply human experience, governed by cosmic forces beyond our control (and also your null pointer exceptions).

It checks your birth chart. It reads the moon. It compiles your code with empathy.

---

## The Full Flow

### 1. PR Opened
When you open a PR, MercuryCI immediately:
- Pulls your **birth chart** from your GitHub profile bio (Rising sign required for full pipeline access)
- Checks the current **moon phase** via the Lunar API
- Queries whether **Mercury is in retrograde**

### 2. The Empathy Compiler

Errors don't just *appear*. They arrive after a 3-second pause, with care:

```
[MERCURYCI] Pausing to gather itself...

  Hey, I know this is hard.
  You have a null pointer exception on line 47.
  You're doing great.

[MERCURYCI] Pausing to gather itself...

  This function hasn't been used in 3 years.
  You don't have to hold onto things forever.

[MERCURYCI] Pausing to gather itself...

  Segmentation fault.
  Mercury is also in retrograde right now, so honestly? Same.
```

### 3. Mercury Retrograde Gate

If Mercury IS in retrograde:

- The merge button is **greyed out**
- Tooltip: `"Not today, bestie."`
- A countdown timer displays: `Mercury direct in X days`
- An optional override exists, labeled: `"I understand the risks (astrological and otherwise)"`

### 4. Slack Integration

MercuryCI posts to `#engineering` automatically:

```
🌑 MercuryCI Alert: Ruby's PR #42 is blocked.
   Mercury retrograde ends in 11 days.
   The compiler says the code "has good bones but needs time."
   Sending healing. 🌿
```

Moon phase is included in every notification header:
- 🌑 New Moon — fresh starts encouraged, risky deploys discouraged
- 🌕 Full Moon — emotions are high, review carefully
- 🌒 Waxing Crescent — good energy for new features
- 🌘 Waning Crescent — time to refactor, release old patterns

### 5. Review Buttons

Reviewers can approve with one of three options:

| Button | Meaning |
|--------|---------|
| ✅ LGTM | Looks good to me (classic) |
| 🌙 The vibes are right | Energetically aligned, ship it |
| 🪐 I defer to the cosmos | I read the code. The stars must decide. |

---

## Setup

```bash
pip install mercuryci

# Add to your .github/workflows/
cp mercuryci.yml .github/workflows/

# Add to your GitHub profile bio:
# ☀️ Scorpio | 🌙 Cancer | ⬆️ Virgo
```

### Environment Variables

```env
MERCURYCI_SLACK_WEBHOOK=your_slack_webhook
MERCURYCI_ASTROLOGY_API_KEY=your_key         # for real-time planetary data
MERCURYCI_BIRTH_CHART_FALLBACK=libra         # used if bio has no chart
MERCURYCI_EMPATHY_LEVEL=high                 # low | medium | high | scorpio
```

---

## Architecture

```
mercuryci/
├── empathy_compiler.py     # Wraps stderr with emotional intelligence
├── mercury_check.py        # Retrograde detection + moon phase
├── birth_chart.py          # Parses GitHub bio for astrological data
├── slack_notifier.py       # Posts cosmic CI updates to Slack
├── review_buttons.py       # Injects custom PR approval UI
└── .github/
    └── workflows/
        └── mercuryci.yml   # The pipeline itself
```

---

## FAQ

**Q: What if my birth chart isn't in my GitHub bio?**
A: The pipeline defaults to Libra rising. We've found this creates the most balanced builds.

**Q: Can I force-merge during retrograde?**
A: You can. The button will say "Override the Cosmos." The pipeline will remember.

**Q: What does "I defer to the cosmos" actually do?**
A: It randomly selects ✅ or ❌ based on the current lunar phase and a weighted RNG seeded with your birth year.

**Q: Is this real?**
A: The empathy is real. The rest is aspirational.

---

*Built with love, TypeScript, and an unhealthy respect for planetary motion.*
