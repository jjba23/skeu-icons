#!/usr/bin/env python3
"""Render the artwork the *standard* contexts need but the app set does not cover.

``categories`` (menu categories) and ``devices`` (volume/device icons) are drawn
by the relief renderer (:mod:`skeu`) as physical objects and written to
``generated/<slug>.png`` (1024 px), which is where the theme keeps its
category and device masters.

    python3 tools/make_context_icons.py            # all
    python3 tools/make_context_icons.py --only categories
"""

from __future__ import annotations

import argparse
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

OUT = ROOT / "generated"


def render_objects(table, label: str) -> None:
    """Render a catalogue table with the relief renderer."""
    from render_skeu import build_generated

    items = [(slug, builder, kwargs) for slug, (builder, kwargs) in sorted(table.items())]
    with Pool(min(10, len(items))) as pool:
        pool.map(build_generated, items)
    print(f"  {label}: {len(items)} icon(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=("categories", "devices"), default=None)
    args = parser.parse_args(argv)

    if args.only in (None, "categories"):
        from skeu.catalog import CATEGORIES as OBJECT_CATEGORIES
        render_objects(OBJECT_CATEGORIES, "categories")
    if args.only in (None, "devices"):
        from skeu.catalog import DEVICES as OBJECT_DEVICES
        render_objects(OBJECT_DEVICES, "devices")
    print(f"done -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
