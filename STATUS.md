# STATUS.md — Renting Your First Apartment: A Friendly Manual

Updated: 2026-11-03

## What was built

A complete beginner manual on renting your first apartment, in warm plain English,
plus a companion static site of printable checklists.

- **`docs/`** — ten Markdown chapters, numbered in the order a first-time renter
  needs them:
  - `00-start-here.md` — how to use the manual; what it is and is *not*
  - `01-budget-real-math.md` — the real monthly number, the move-in bill, budget
    worksheet, cost creeps
  - `02-applications-and-credit.md` — what's on an application, how credit and
    screening work, the "rough credit" playbook, listing-scam red flags
  - `03-lease-clause-by-clause.md` — a guided read of every lease section, with
    red-flag clauses and a pre-signature sanity check
  - `04-walkthrough-checklists.md` — apartment tour list and the full move-in
    inspection form (the deposit-protection walkthrough)
  - `05-roommates.md` — co-tenancy options, a one-page roommate agreement,
    money rules, early-exit and conflict-escalation advice
  - `06-repairs-and-records.md` — repair-request template, the repair log,
    follow-up ladder, tenant-side maintenance, monthly photo habit
  - `07-deposit-recovery.md` — the deposit timeline, deep-clean checklist,
    move-out walkthrough, inquiry letter, exhibit list, wear-and-tear test
  - `08-moving-in.md` — two-week countdown, utilities order, packing method,
    move-in day hour-by-hour, first-week setup and kit
  - `09-glossary.md` — rental terms defined in plain English

- **`site/`** — static HTML site (no build step, no frameworks, no external
  requests) with five pages:
  - `index.html` — hub linking to all printables
  - `budget.html` — monthly budget + move-in-cost worksheet, printable
  - `walkthrough.html` — tour checklist + move-in inspection form, printable
  - `moveout.html` — countdown, deep clean, move-out walkthrough, deposit
    inquiry letter, printable
  - `firstweek.html` — utilities, new-place kit, the seven days, printable
  - Shared `style.css` includes a dedicated `@media print` block (checkbox
    glyphs, one-card-per-page breaks, headers/nav hidden when printing).

- **`tests/validate.py`** — 163-check validation suite (details below).

- **`README.md`** and **`LICENSE`** (MIT, copyright "Copyright (c) 2026
  Asdale Dynamics, LLC").

## How to run/verify

- Read the manual: open `docs/00-start-here.md` in any Markdown reader/editor.
- Use the site: open `site/index.html` in any browser (double-click the file);
  each checklist page has a "Print this page" button.
- Run the test suite: `python3 tests/validate.py` (Python 3.8+; no dependencies).

## Verification results

`python3 tests/validate.py` — **PASS: 163 checks, 0 failures** (final run).

The suite verifies:
- all ten expected chapter files exist with headings, structure, and required
  "not legal advice" wording; the start-here index table lists every chapter;
- internal links in all Markdown resolve to real files;
- no stray non-English (CJK) text, no leftover drafting placeholders, no
  secret-looking strings (key/secret/password patterns, long token-like
  strings, private-key blocks) anywhere in docs, site, README, or LICENSE;
- all HTML pages are well-formed (matched tag nesting, DOCTYPE, title, charset,
  stylesheet linked), with a print stylesheet and checkbox glyph present;
- all internal site links resolve; every checklist page contains its four
  required sections and a wired-up print button with `no-print` markup;
- no external scripts/images/iframes or tracker strings in any page;
- LICENSE contains the exact required copyright line and MIT grant text;
- README credits Asdale Dynamics, LLC, includes the not-legal-advice note, and
  documents the test command.

## Known gaps / limitations

- **Not legal advice, by design.** Deposit deadlines, notice periods, repair
  rights, late-fee caps, screening rules, and eviction process all vary by
  state and city. The manual consistently points readers to official local
  tenant resources instead of stating jurisdiction-specific rules.
- The site is intentionally dependency-free static HTML; there is no PDF
  generation — printing to PDF is expected via the browser (tested semantics
  only, in-test, not in a real browser here).
- The test suite is a validation script rather than a rendering test; it
  checks structure, links, and content, not visual layout.
- Chapters use U.S./general-market conventions (pay stubs, credit reports,
  renter's insurance) with caveats; readers outside that context will need to
  map some specifics.
- Example dollar figures are illustrative ranges, not market data.
