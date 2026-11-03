# Renting Your First Apartment: A Friendly Manual

The beginner-friendly guide to renting your first place — written the way a
friend would explain it: plain English, step by step, never condescending.
Includes a printable-checklist static site.

**What's inside:**

- **`docs/`** — the manual, ten Markdown chapters in the order you'll need them:
  1. Budgeting the *real* math (the move-in bill and the true monthly number)
  2. Applications and credit talk (including the "my credit is rough" playbook)
  3. Reading the lease clause by clause
  4. Walkthrough checklists (tour + the deposit-protecting move-in inspection)
  5. Roommates: money, agreements, and conflict handled early
  6. Repairs and the paper trail that pays
  7. Getting your security deposit back
  8. Moving in: utilities, logistics, and the first week
  9. Glossary of rental words in plain English

- **`site/`** — a small static website (no frameworks, no trackers, no build step)
  with printable versions of the checklists: budget worksheet, walkthroughs,
  move-out/deposit packet, and first-week setup. Open `site/index.html` in a
  browser and hit Ctrl/Cmd+P.

- **`tests/`** — a validation script that checks the manual and site for broken
  links, malformed HTML, missing sections, leftover drafting artifacts, and
  secret-looking strings.

**How to use it:**

- Read the manual: start at `docs/00-start-here.md` and go chapter by chapter.
- Print the checklists: open `site/index.html`, click a checklist, print it.
- Validate everything: `python3 tests/validate.py` (requires Python 3.8+).

**Honest notes:**

- This is **education, not legal advice**. Deposit deadlines, notice periods, and
  repair rules vary by state and city; the manual tells you when to check your
  local official tenant resources rather than trusting a general guide.
- Local-first and private: the site loads nothing from the network and contains
  no trackers, analytics, or secrets.

Made by **Asdale Dynamics, LLC** — beginner-friendly guides and practical tools.
MIT licensed; see `LICENSE`.
