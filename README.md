# MercuryCI 🪐 - April Fools Hackathon
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

## How your sign is resolved

MercuryCI uses this priority order to find your sign:

1. **Saved config** — `~/.mercuryci/config.json` (fastest, set once)
2. **GitHub bio** — parsed automatically if it contains a zodiac sign
3. **Interactive prompt** — if neither of the above works, you'll be asked on first run

The prompt lets you enter either your **sun sign directly** or your **birth month and day** (MercuryCI converts the date to a sign automatically).

```
MercuryCI couldn't find a zodiac sign for @you.
The pipeline needs this to function at full cosmic capacity.

How would you like to provide it?
1. Enter my sun sign directly
2. Enter my birth month and day
3. Skip for now (defaults to Libra)
```

Your answer is saved to `~/.mercuryci/config.json` so you're never asked again.

### Changing your sign later

```bash
python settings.py              # uses your current gh auth account
python settings.py --user ruby  # for a specific username
```

Settings menu options:
- View current profile
- Set sign manually
- Set sign by birth date
- Clear saved profile

---

## Browser Extension

The extension makes the review buttons real — injected directly into the GitHub PR sidebar.

### Install (Chrome / Edge)

1. Go to `chrome://extensions` and enable **Developer mode**
2. Click **Load unpacked** and select the `extension/` folder
3. Click the 🪐 icon in your toolbar
4. Paste a GitHub token with `repo` scope ([create one here](https://github.com/settings/tokens/new?scopes=repo&description=MercuryCI))
5. Enter your sun sign or birth date — saved locally, never leaves your browser

### What the extension does

On any GitHub PR page, a **MercuryCI panel** appears in the right sidebar showing:
- Current moon phase + guidance
- Mercury retrograde countdown (if active)
- Three review buttons that call the GitHub API directly:

| Button | GitHub review event |
|--------|-------------------|
| ✅ LGTM | `APPROVE` |
| 🌙 The vibes are right | `APPROVE` with cosmic note |
| 🪐 I defer to the cosmos | `APPROVE` or `REQUEST_CHANGES` — decided by moon phase weighted RNG |

"Defer to cosmos" weights: Full Moon = 70% approve, retrograde = −15% penalty.

### Extension files

```
extension/
├── manifest.json           # Manifest V3, targets github.com/*/pull/*
└── src/
    ├── cosmic.js           # Moon phase + retrograde logic (pure JS)
    ├── github_api.js       # GitHub REST API wrapper
    ├── content.js          # Injects panel into PR sidebar
    ├── styles.css          # Panel + button styles
    ├── popup.html          # Settings popup UI
    ├── popup.js            # Token auth, sign picker, birthdate → sign
    └── background.js       # Service worker, re-injects on install
```

---

## Architecture

```
mercuryci/
├── empathy_compiler.py     # Wraps stderr with emotional intelligence
├── mercury_check.py        # Retrograde detection + moon phase
├── birth_chart.py          # Sign resolution: config → bio → prompt
├── config.py               # Reads/writes ~/.mercuryci/config.json
├── settings.py             # Interactive settings menu (CLI)
├── slack_notifier.py       # Posts cosmic CI updates to Slack
├── review_buttons.py       # Review logic (used by extension + pipeline)
├── extension/              # Chrome/Edge browser extension
└── .github/
    └── workflows/
        └── mercuryci.yml   # The CI/CD pipeline
```

---

## FAQ

**Q: What if my birth chart isn't in my GitHub bio?**
A: You'll be prompted on first run to enter your sign or birth date. It saves to `~/.mercuryci/config.json` and never asks again.

**Q: Can I change my sign later?**
A: Yes. Run `python settings.py` for the full settings menu.

**Q: Can I force-merge during retrograde?**
A: You can. The button will say "Override the Cosmos." The pipeline will remember.

**Q: What does "I defer to the cosmos" actually do?**
A: It randomly selects ✅ or ❌ based on the current lunar phase and a weighted RNG seeded with your birth year.

**Q: Is this real?**
A: The empathy is real. The rest is aspirational.

---

*Built with love, TypeScript, and an unhealthy respect for planetary motion.*
