#!/usr/bin/env python3
"""Validation tests for the Rent-Your-First-Apartment-Guide repo.

Checks that the Markdown manual, the static HTML site, and the repo metadata are
complete and internally consistent: every file referenced by the handbook index
exists, all internal links resolve, every HTML page is well-formed with its print
stylesheet and printable checklists present, no stray CJK/dropped-in non-English
text survived, and no secret-looking strings are committed.

Run with:  python3 tests/validate.py
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

failures: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


# ---------------------------------------------------------------- docs ------

EXPECTED_CHAPTERS = [
    "00-start-here.md",
    "01-budget-real-math.md",
    "02-applications-and-credit.md",
    "03-lease-clause-by-clause.md",
    "04-walkthrough-checklists.md",
    "05-roommates.md",
    "06-repairs-and-records.md",
    "07-deposit-recovery.md",
    "08-moving-in.md",
    "09-glossary.md",
]


def test_chapters_exist() -> None:
    for name in EXPECTED_CHAPTERS:
        check((DOCS / name).is_file(), f"missing docs file: {name}")


def test_chapters_have_heading_and_disclaimer() -> None:
    for name in EXPECTED_CHAPTERS:
        text = (DOCS / name).read_text(encoding="utf-8")
        check(text.startswith("# "), f"{name}: does not start with an H1")
        check("## " in text or "---" in text, f"{name}: has no section structure")
    # The two chapters where the disclaimer matters most state it explicitly.
    for name, phrase in [
        ("00-start-here.md", "not legal advice"),
        ("03-lease-clause-by-clause.md", "Not legal advice"),
        ("07-deposit-recovery.md", "Not legal advice"),
    ]:
        text = (DOCS / name).read_text(encoding="utf-8")
        check(phrase.lower() in text.lower(),
              f"{name}: missing the 'not legal advice' wording")


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+)\)")


def test_internal_links_resolve() -> None:
    for md in sorted(DOCS.glob("*.md")) + sorted(ROOT.glob("*.md")):
        for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_part = urlparse(target).path
            if not path_part:
                continue  # pure anchor link
            resolved = (md.parent / path_part).resolve()
            check(resolved.exists(),
                  f"{md.name}: broken internal link -> {target}")


def test_start_here_index_table_matches() -> None:
    text = (DOCS / "00-start-here.md").read_text(encoding="utf-8")
    for name in EXPECTED_CHAPTERS:
        check(f"`{name}`" in text,
              f"00-start-here.md: chapters table does not reference {name}")


def test_no_stray_cjk_or_placeholder_text() -> None:
    global checks
    cjk = re.compile(r"[\u4e00-\u9fff]")
    for md in sorted(DOCS.glob("*.md")) + sorted(SITE.glob("*.html")):
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if cjk.search(line):
                failures.append(f"{md.name}:{i}: non-English characters found")
                checks += 1


def test_no_todos_or_secrets() -> None:
    global checks
    secret_patterns = [
        re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9]{8,}"),
        re.compile(r"(?i)secret\s*[:=]\s*['\"][A-Za-z0-9]{8,}"),
        re.compile(r"(?i)password\s*[:=]\s*['\"][A-Za-z0-9]{8,}"),
        re.compile(r"\b[A-Za-z0-9+/]{40,}\b"),
        re.compile(r"ghp_[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ]
    scan_files = [
        *sorted(DOCS.glob("*.md")),
        *sorted(SITE.glob("*.html")),
        *ROOT.glob("*.md"),
        ROOT / "LICENSE",
    ]
    todo = re.compile(r"\b(TODO|FIXME|XXX)\b")
    for f in scan_files:
        if not f.is_file():
            continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for pat in secret_patterns:
                if pat.search(line):
                    failures.append(f"{f.name}:{i}: secret-looking string found")
                    checks += 1
            if todo.search(line) and "tests/" not in str(f):
                failures.append(f"{f.name}:{i}: TODO/FIXME placeholder left in")
                checks += 1


def test_no_unfinished_sentences() -> None:
    """Catches leftover drafting artifacts like doubled spaces inside words."""
    for md in sorted(DOCS.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        for snippet in ["ing-ing", "-out-out", "for-notice"]:
            check(snippet not in text, f"{md.name}: drafting artifact '{snippet}'")


# ---------------------------------------------------------------- site ------

class PageParser(HTMLParser):
    """Collects tag + link data with a tiny amount of strictness."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.tags: list[str] = []
        self.stack: list[str] = []
        self.void_tags = {
            "area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr",
        }

    def handle_starttag(self, tag: str, attrs) -> None:
        self.tags.append(tag)
        if tag in self.void_tags:
            return
        self.stack.append(tag)
        for name, value in attrs:
            if name == "href" and value:
                self.links.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.void_tags:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.bad_nesting = True


def parse_page(path: Path) -> tuple[PageParser, list[str]]:
    text = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.bad_nesting = False
    parser.feed(text)
    problems: list[str] = []
    if parser.bad_nesting:
        problems.append("malformed tag nesting")
    if parser.stack:
        problems.append(f"unclosed tags: {parser.stack}")
    return parser, problems


def test_pages_structural() -> None:
    pages = sorted(SITE.glob("*.html"))
    check(len(pages) >= 5, f"site/ should have at least 5 html pages, found {len(pages)}")
    for page in pages:
        parser, problems = parse_page(page)
        for problem in problems:
            failures.append(f"{page.name}: {problem}")
            checks += 1
        raw = page.read_text(encoding="utf-8")
        check(raw.lstrip().lower().startswith("<!doctype html>"),
              f"{page.name}: missing DOCTYPE")
        check("<title>" in raw, f"{page.name}: missing <title>")
        check('charset="utf-8"' in raw or "charset=utf-8" in raw,
              f"{page.name}: missing charset declaration")
        check('link rel="stylesheet"' in raw and "style.css" in raw,
              f"{page.name}: print stylesheet not linked")
    css = (SITE / "style.css").read_text(encoding="utf-8")
    check("@media print" in css, "style.css: missing print stylesheet block")
    check("\\2610" in css or "\u2610" in css,
          "style.css: missing printable checkbox glyph")


def test_internal_site_links_resolve() -> None:
    for page in sorted(SITE.glob("*.html")):
        parser, _ = parse_page(page)
        for href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (SITE / href).resolve()
            check(resolved.exists(),
                  f"{page.name}: broken link -> {href}")


CHECKLIST_PAGES = {
    "budget.html": ["A. Monthly budget", "B. Move-in bill calculator",
                    "C. Rule-of-thumb reference table"],
    "walkthrough.html": ["A. The Apartment Tour", "B. Move-In Inspection"],
    "moveout.html": ["A. The Countdown", "B. The Deep Clean",
                     "C. Move-Out Walkthrough", "D. Deposit Inquiry Letter"],
    "firstweek.html": ["A. Utilities", "B. The New-Place Kit", "C. The Seven Days",
                       "D. Move-out prep began today"],
}


def test_checklist_content() -> None:
    for page, sections in CHECKLIST_PAGES.items():
        raw = (SITE / page).read_text(encoding="utf-8")
        for section in sections:
            check(section in raw, f"{page}: missing section '{section}'")


def test_every_page_printable() -> None:
    for page in sorted(SITE.glob("*.html")):
        if page.name == "index.html":
            continue
        raw = page.read_text(encoding="utf-8")
        check("window.print()" in raw or "print()" in raw,
              f"{page.name}: no print button wired up")
        check("no-print" in raw, f"{page.name}: nothing marked no-print")


def test_no_external_trackers() -> None:
    """Static and local-first: no remote scripts, no analytics, no fonts loaded."""
    for page in sorted(SITE.glob("*.html")):
        raw = page.read_text(encoding="utf-8")
        external_src = re.findall(r'<(?:script|img|iframe)[^>]+src="(http[^"]+)"', raw)
        check(not external_src,
              f"{page.name}: external resources found: {external_src}")
        check("analytics" not in raw.lower() and "tagmanager" not in raw.lower(),
              f"{page.name}: tracker-looking strings found")


# -------------------------------------------------------------- metadata ----

def test_license_exact() -> None:
    lic = ROOT / "LICENSE"
    check(lic.is_file(), "LICENSE file missing")
    if lic.is_file():
        text = lic.read_text(encoding="utf-8")
        check("Copyright (c) 2026 Asdale Dynamics, LLC" in text,
              "LICENSE: copyright line is not exactly the required string")
        check("Permission is hereby granted, free of charge" in text,
              "LICENSE: does not look like the MIT license text")


def test_readme_credit() -> None:
    readme = ROOT / "README.md"
    check(readme.is_file(), "README.md missing")
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        check("Asdale Dynamics, LLC" in text,
              "README.md: does not credit Asdale Dynamics, LLC")
        check("legal advice" in text.lower(),
              "README.md: no 'not legal advice' note")
        check("python3 tests/validate.py" in text,
              "README.md: test run instructions missing")


def main() -> int:
    test_chapters_exist()
    test_chapters_have_heading_and_disclaimer()
    test_internal_links_resolve()
    test_start_here_index_table_matches()
    test_no_stray_cjk_or_placeholder_text()
    test_no_todos_or_secrets()
    test_no_unfinished_sentences()
    test_pages_structural()
    test_internal_site_links_resolve()
    test_checklist_content()
    test_every_page_printable()
    test_no_external_trackers()
    test_license_exact()
    test_readme_credit()

    print(f"Rent-a-first-apartment guide: {checks} checks run.")
    if failures:
        print(f"FAILED ({len(failures)}):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("All good — docs, site, and metadata validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
