#!/usr/bin/env python3
"""Write the numbers README.org quotes from the theme on disk.

Hand-typed counts drift: an icon is added, the README keeps the old number, and
nothing fails.  This script derives every count the README states from the tree
itself — the six context totals and their sum, the symbolic layer and its
per-context rows, the plain scalable layer, the drawn app and project icons, the
directories declared in ``index.theme`` and the number of themes — and rewrites
only those numbers, leaving the prose around them alone.

    python3 tools/make_readme_counts.py            # rewrite the numbers
    python3 tools/make_readme_counts.py --check    # exit 1 if the README drifted

``maak check`` runs the check, so a stale README fails the build the same way a
stale gallery does.  If a sentence the script knows about has been reworded it
says which one instead of silently skipping it, and it writes nothing at all
until every count it quotes has a home.

Two counts stay hand-written because the theme cannot prove them: the 377 file
extensions (the ``application-x-<ext>`` fallbacks are many more than there are
extensions) and the 164 icons drawn for the applications installed on this
machine (``app-icons/index.json`` is a snapshot of that machine's launcher
entries, not a property of the pack).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.org"
THEME = ROOT / "skeu-icons"
CONTEXTS = ("apps", "places", "mimetypes", "emblems", "categories", "devices")
#: The symbolic layer and the plain scalable layer drawn from it (see
#: tools/make_symbolic.py and tools/make_plain.py).
SYMBOLIC_CONTEXTS = ("actions", "categories", "devices", "emotes", "legacy",
                     "mimetypes", "places", "status", "ui")
PLAIN_CONTEXTS = ("actions", "emotes", "legacy", "status", "ui")


class ReadmeError(Exception):
    """A sentence the script anchors on is missing or appears twice."""


def names_in(directory: Path, suffix: str = "*.png") -> int:
    """How many distinct icon names a directory holds."""
    return len({path.stem for path in directory.glob(suffix)})


def declared_directories() -> int:
    """How many directories ``index.theme`` declares, fixed and scaled."""
    header: dict[str, str] = {}
    section: str | None = None
    for line in (THEME / "index.theme").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
        elif "=" in line and section in (None, "Icon Theme"):
            key, value = line.split("=", 1)
            header[key.strip()] = value.strip()
    return sum(len([item for item in header.get(key, "").split(",") if item.strip()])
               for key in ("Directories", "ScaledDirectories"))


def set_counts(path: Path) -> int:
    """The ``count`` field of an ``app-icons``-style index."""
    return int(json.loads(path.read_text(encoding="utf-8"))["count"])


def counts() -> dict:
    """Every number the README quotes, read from the tree."""
    contexts = {context: names_in(THEME / "512x512" / context) for context in CONTEXTS}
    symbolic = {context: names_in(THEME / "symbolic" / context, "*.svg")
                for context in SYMBOLIC_CONTEXTS}
    plain = {context: names_in(THEME / "scalable" / context, "*.svg")
             for context in PLAIN_CONTEXTS}
    return {
        "contexts": contexts,
        "names": sum(contexts.values()),
        "symbolic": symbolic,
        "symbolic_total": sum(symbolic.values()),
        "plain": plain,
        "plain_total": sum(plain.values()),
        "app_icons": set_counts(ROOT / "app-icons" / "index.json"),
        "project_icons": set_counts(ROOT / "project-icons" / "index.json"),
        "directories": declared_directories(),
        "themes": 1 + len(list(ROOT.glob("skeu-icons-*/index.theme"))),
    }


def grouped(number: int) -> str:
    """``1914`` as the README writes it: ``1 914``."""
    return f"{number:,}".replace(",", " ")


def badged(number: int) -> str:
    """The same grouping, escaped for a shields.io badge path."""
    return grouped(number).replace(" ", "%20")


def cell(match: re.Match[str], number: int) -> str:
    """Right-align a count in the table cell the match already lines up."""
    prefix, digits = match.group(1), match.group(2)
    width = len(prefix) - len(prefix.rstrip(" ")) + len(digits)
    return prefix.rstrip(" ") + str(number).rjust(width) + match.group(3)


def plain_number(match: re.Match[str], number: int) -> str:
    """Replace the number in a run of prose, keeping the sentence around it."""
    return f"{match.group(1)}{number}{match.group(3)}"


def two_numbers(match: re.Match[str], first: int, second: int) -> str:
    """A sentence that names two counts (the ``maak`` task comment)."""
    return f"{match.group(1)}{first}{match.group(3)}{second}{match.group(5)}"


def slots(values: dict) -> list[tuple[str, str, callable]]:
    """``(label, pattern, builder)`` for every count the README quotes.

    Each pattern must match exactly once: the group before and after the number
    is what keeps the script on the right sentence when the prose changes.
    """
    names, themes = values["names"], values["themes"]
    symbolic, plain = values["symbolic_total"], values["plain_total"]
    apps, projects = values["app_icons"], values["project_icons"]
    found: list[tuple[str, str, callable]] = [
        # the one-line description, the badge, the intro bullet and the total
        ("meta description",
         r"(A skeuomorphic icon theme for Linux desktops: )([\d ]+)( icon names across six freedesktop contexts)",
         lambda m: f"{m.group(1)}{grouped(names)}{m.group(3)}"),
        ("icons badge",
         r"(img\.shields\.io/badge/icons-)([\d%]+)(-informational\.svg)",
         lambda m: f"{m.group(1)}{badged(names)}{m.group(3)}"),
        ("intro bullet",
         r"(\*Complete, not curated\.\*\s+)([\d ]+)( icon names across all six freedesktop)",
         lambda m: f"{m.group(1)}{grouped(names)}{m.group(3)}"),
        ("totals sentence",
         r"(That is )([\d ]+)( names, shipped at )",
         lambda m: f"{m.group(1)}{grouped(names)}{m.group(3)}"),
        ("themes badge",
         r"(img\.shields\.io/badge/themes-)(\d+)(-informational\.svg)",
         lambda m: plain_number(m, themes)),
        # the six contexts and the total they add up to
        ("directories declared",
         r"(=scalable/= SVGs — )(\d+)( directories declared in)",
         lambda m: plain_number(m, values["directories"])),
        # the drawn application and project icons
        ("app icons drawn",
         r"(\| )(\d+)( drawn icons, each linked under every name it is asked by)",
         lambda m: plain_number(m, apps)),
        ("app icons size",
         r"(Twenty-four of the )(\d+)( application icons)",
         lambda m: plain_number(m, apps)),
        ("app-icons row",
         r"(\| =app-icons/=\s+\|\s+)(\d+)( GUI app icons)",
         lambda m: cell(m, apps)),
        ("project icons size",
         r"(A selection of the )(\d+)( project icons)",
         lambda m: plain_number(m, projects)),
        ("project-icons row",
         r"(\| =project-icons/=\s+\|\s+)(\d+)( icons for project folders)",
         lambda m: cell(m, projects)),
        ("project icons installed",
         r"(and )(\d+)( for personal)",
         lambda m: plain_number(m, projects)),
        # the symbolic layer: its total, its per-context rows, and the plain
        # scalable layer drawn beside it
        ("symbolic bullet",
         r"(A )(\d+)(-name symbolic layer)",
         lambda m: plain_number(m, symbolic)),
        ("symbolic copies",
         r"(of fourteen copies of )(\d+)( files)",
         lambda m: plain_number(m, symbolic)),
        ("symbolic table",
         r"(\| =symbolic/<context>=\s+\|\s+)(\d+)(\s+\|)",
         lambda m: cell(m, symbolic)),
        ("symbolic task",
         r"(redraw the )(\d+)( symbolic icons \+ )(\d+)( plain scalable ones)",
         lambda m: two_numbers(m, symbolic, plain)),
        ("symbolic script",
         r"(the symbolic layer \()(\d+)( names\))",
         lambda m: plain_number(m, symbolic)),
        ("plain scalable bullet",
         r"(plus )(\d+)( plain scalable icons)",
         lambda m: plain_number(m, plain)),
        ("plain scalable script",
         r"(the un-suffixed scalable icons \()(\d+)(\))",
         lambda m: plain_number(m, plain)),
        ("plain actions row",
         r"(\| =scalable/actions=\s+\|\s+)(\d+)(\s+\|)",
         lambda m: cell(m, values["plain"]["actions"])),
        ("plain status row",
         r"(\| =scalable/status=\s+\|\s+)(\d+)(\s+\|)",
         lambda m: cell(m, values["plain"]["status"])),
        ("plain emotes row",
         r"(\| =scalable/emotes=\s+\|\s+)(\d+)(\s+\|)",
         lambda m: cell(m, values["plain"]["emotes"])),
        ("plain ui/legacy row",
         r"(\| =scalable/ui=, =legacy=\s+\|\s+)(\d+)(\s+\|)",
         lambda m: cell(m, values["plain"]["ui"] + values["plain"]["legacy"])),
    ]
    for context in CONTEXTS:
        found.append((
            f"{context} row",
            rf"(\| ={context}=\s+\|\s+)(\d+)(\s+\|)",
            lambda m, context=context: cell(m, values["contexts"][context]),
        ))
    return found


def rewrite(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """``(new text, [(label, old, new)])``; raises if a sentence has moved."""
    changed: list[tuple[str, str, str]] = []
    for label, pattern, build in slots(counts()):
        matches = list(re.finditer(pattern, text))
        if len(matches) != 1:
            raise ReadmeError(
                f"README.org: the {label} sentence matched {len(matches)} times, "
                "expected once - reword it back or teach this script the new one")
        match = matches[0]
        replacement = build(match)
        if replacement != match.group(0):
            changed.append((label, match.group(0), replacement))
            text = text[:match.start()] + replacement + text[match.end():]
    return text, changed


def drift(text: str | None = None) -> list[str]:
    """Problems for ``maak check``: stale numbers, or sentences it cannot find."""
    text = README.read_text(encoding="utf-8") if text is None else text
    try:
        _, changed = rewrite(text)
    except ReadmeError as error:
        return [f"{error} (run: python3 tools/make_readme_counts.py)"]
    return [f"README.org {label}: {old!r} should be {new!r} "
            f"(run: python3 tools/make_readme_counts.py)"
            for label, old, new in changed]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report stale numbers instead of writing them")
    args = parser.parse_args(argv)

    text = README.read_text(encoding="utf-8")
    try:
        new_text, changed = rewrite(text)
    except ReadmeError as error:
        print(f"  {error}", file=sys.stderr)
        return 1

    if args.check:
        if changed:
            for label, old, new in changed:
                print(f"  README.org {label}: {old!r} should be {new!r}", file=sys.stderr)
            print(f"\n{len(changed)} stale count(s) - run: python3 tools/make_readme_counts.py",
                  file=sys.stderr)
            return 1
        print("ok: README.org counts match the theme")
        return 0

    if not changed:
        print("ok: README.org counts were already current")
        return 0
    README.write_text(new_text, encoding="utf-8")
    for label, old, new in changed:
        print(f"  {label}: {old!r} -> {new!r}")
    print(f"wrote {len(changed)} count(s) to README.org")
    return 0


if __name__ == "__main__":
    sys.exit(main())
