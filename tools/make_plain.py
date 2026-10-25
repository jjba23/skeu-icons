#!/usr/bin/env python3
"""Draw the un-suffixed icons for the contexts the pack never had artwork for.

``apps``, ``places``, ``mimetypes``, ``emblems``, ``categories`` and ``devices``
ship as relief-rendered bitmaps.  ``actions``, ``status``, ``emotes``, ``ui`` and
``legacy`` had nothing: a GTK 3 app asking for ``list-add`` (not
``list-add-symbolic``) fell through to AdwaitaLegacy, or to hicolor and nothing at
all.  These are the same Aqua glyphs as the symbolic layer, drawn once in ink and
written as scalable SVG:

    skeu-icons/scalable/actions/list-add.svg

Scalable is the honest choice here: the glyph is a 16-unit drawing, so a toolkit
renders it at exactly the pixel grid it asks for, and one file covers every size
a menu, a toolbar or a HiDPI dock needs.

    python3 tools/make_plain.py            # write every missing context
    python3 tools/make_plain.py --check    # nothing missing, nothing stale
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_symbolic import base_name, read_contract, render  # noqa: E402

THEME = ROOT / "skeu-icons"
OUT = THEME / "scalable"

#: Contexts that keep their relief bitmaps; everything else is drawn here.
RASTER_CONTEXTS = frozenset({"apps", "places", "mimetypes", "emblems",
                             "categories", "devices"})


def plain_contexts() -> list[str]:
    """Contexts that need a scalable drawing, in contract order."""
    seen: list[str] = []
    for context, _name in read_contract():
        if context not in RASTER_CONTEXTS and context not in seen:
            seen.append(context)
    return seen


def plan(only: str | None = None) -> list[tuple[str, str, Path]]:
    """``[(context, symbolic source name, plain path)]`` for every icon to draw.

    Adwaita spells the same file two ways - ``foo-rtl-symbolic.svg`` and
    ``foo-symbolic-rtl.svg`` - and both fold to ``foo-rtl.svg`` here, so the
    first spelling is kept and the second is dropped rather than written twice.
    """
    items = []
    taken: set[Path] = set()
    for context, name in read_contract():
        if context in RASTER_CONTEXTS or (only and context != only):
            continue
        base, mirrored = base_name(name)
        suffix = "-rtl" if mirrored else ""
        path = OUT / context / f"{base}{suffix}.svg"
        if path in taken:
            continue
        taken.add(path)
        items.append((context, name, path))
    return items


def build(only: str | None = None, quiet: bool = False) -> int:
    written = 0
    items = plan(only)
    for context, name, path in items:
        text = render(context, name, title=path.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_text() != text:
            path.write_text(text)
            written += 1
    if not quiet:
        print(f"plain: {len(items)} icon(s), {written} written -> {OUT}")
    return 0


def check(only: str | None = None) -> list[str]:
    problems: list[str] = []
    items = plan(only)
    for context, name, path in items:
        if not path.is_file():
            problems.append(f"{path.relative_to(ROOT)}: missing - run make_plain.py")
            continue
        if path.read_text() != render(context, name, title=path.name):
            problems.append(f"{path.relative_to(ROOT)}: stale - run make_plain.py")
    listed = {path for _context, _name, path in items}
    for path in sorted(OUT.rglob("*.svg")):
        if path.parent.name in RASTER_CONTEXTS or path in listed:
            continue
        problems.append(f"{path.relative_to(ROOT)}: not in the parity contract")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", choices=plain_contexts(), help="draw one context")
    parser.add_argument("--check", action="store_true",
                        help="do not write; fail if anything is missing or stale")
    args = parser.parse_args(argv)

    if args.check:
        problems = check(args.only)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) found", file=sys.stderr)
            return 1
        print(f"ok: {len(plan(args.only))} plain icons match the catalogue")
        return 0
    return build(args.only)


if __name__ == "__main__":
    sys.exit(main())
