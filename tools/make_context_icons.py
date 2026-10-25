#!/usr/bin/env python3
"""Render the artwork the *standard* contexts need but the app set does not cover.

``categories`` (menu categories) and ``devices`` (volume/device icons) are drawn
by the relief renderer (:mod:`skeu`) as physical objects and written to
``generated/<slug>.png`` (1024 px), which is where the theme keeps its
category and device masters.  ``--install`` then distributes those masters into
the theme at every size it ships, ``@2x`` included:

    skeu-icons/48x48/devices/phone-old.png
    skeu-icons/48x48@2x/devices/phone-old.png

    python3 tools/make_context_icons.py            # all, masters only
    python3 tools/make_context_icons.py --only categories
    python3 tools/make_context_icons.py --install  # + the theme's size set
"""

from __future__ import annotations

import argparse
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

OUT = ROOT / "generated"
THEME = ROOT / "skeu-icons"

#: Sizes the theme ships as bitmaps; ``@2x`` doubles each one.
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)


def render_objects(table, label: str) -> None:
    """Render a catalogue table with the relief renderer."""
    from render_skeu import build_generated

    items = [(slug, builder, kwargs) for slug, (builder, kwargs) in sorted(table.items())]
    with Pool(min(10, len(items))) as pool:
        pool.map(build_generated, items)
    print(f"  {label}: {len(items)} icon(s)")


def install(table, context: str) -> int:
    """Write every master in TABLE into the theme's size set for CONTEXT."""
    from render_skeu import resize

    written = 0
    for slug in sorted(table):
        master = OUT / f"{slug}.png"
        if not master.is_file():
            print(f"  no master: {master.relative_to(ROOT)}", file=sys.stderr)
            continue
        with Image.open(master) as source:
            image = source.convert("RGBA")
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                target = THEME / f"{size}x{size}{suffix}" / context / f"{slug}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                resize(image, size * factor).save(target)
                written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=("categories", "devices"), default=None)
    parser.add_argument("--install", action="store_true",
                        help="also write the theme's size set from the masters")
    args = parser.parse_args(argv)

    tables = []
    if args.only in (None, "categories"):
        from skeu.catalog import CATEGORIES as OBJECT_CATEGORIES
        render_objects(OBJECT_CATEGORIES, "categories")
        tables.append((OBJECT_CATEGORIES, "categories"))
    if args.only in (None, "devices"):
        from skeu.catalog import DEVICES as OBJECT_DEVICES
        render_objects(OBJECT_DEVICES, "devices")
        tables.append((OBJECT_DEVICES, "devices"))
    print(f"done -> {OUT}")
    if args.install:
        for table, context in tables:
            count = install(table, context)
            print(f"  installed {count} file(s) into the theme's {context} contexts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
