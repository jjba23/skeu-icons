#!/usr/bin/env python3
"""Dress the places icons the era drew with its own artwork.

The *places* context is mostly the pack's own drawings - the blue, graphite,
brown, cyan and violet folders are objects painted here, not Apple's files.  A
few names in it are not folders at all, though: they are the one piece of the
desktop that has to look like the object it stands for, the wastebasket.  Apple
published that object - the wire-mesh basket on its ring, empty and with the
day's paper in it - and a desktop dressed as Leopard wants the mesh basket, not
a look-alike drawn in the same spirit.

``PLACES`` maps theme place names onto catalogued artwork in ``library/places``
(see ``library/README.org`` for its provenance), and this step writes each one
at every size the theme ships, ``@2x`` included, with a
``skeu-icons/scalable/places/<name>.svg`` wrapper beside it.  Every other name
in the context keeps the pack's drawing.

    python3 tools/make_theme_places.py            # install + scalable wrappers
    python3 tools/make_theme_places.py --check    # report drift, write nothing
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_theme_mimes import svg_wrapper  # noqa: E402
from render_skeu import resize, save_png, save_text  # noqa: E402

THEME = ROOT / "skeu-icons"
LIBRARY = ROOT / "library"
PLACE_DIR = LIBRARY / "places"
CATALOGUE = LIBRARY / "places.json"

#: Sizes the theme ships as bitmaps; every name is mirrored into ``@2x``.
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "places"
SCALABLE = THEME / "scalable" / CONTEXT

#: The size the artwork is resampled up to before it is cut down again; the
#: sources are 128 px, so this only gives every size a common grid to work on.
MASTER = 512

#: ``theme place name -> artwork stem in library/places``.  Both spellings of
#: the empty basket are here on purpose: the spec name is ``user-trash`` and
#: toolkits that predate it ask for ``user-trash-empty``, and a desktop that
#: asks for the one this table forgot shows a folder where the bin should be.
PLACES: dict[str, str] = {
    "user-trash": "user-trash",
    "user-trash-empty": "user-trash",
    "user-trash-full": "user-trash-full",
}


def catalogue() -> dict[str, dict]:
    """``{stem: record}`` for the era places, from ``library/places.json``."""
    if not CATALOGUE.is_file():
        return {}
    return {record["stem"]: record for record in json.loads(CATALOGUE.read_text())}


def masters(wanted: set[str]) -> dict[str, Image.Image]:
    """Resample every place stem the table asks for, once each."""
    out: dict[str, Image.Image] = {}
    for stem in sorted(wanted):
        path = PLACE_DIR / f"{stem}.png"
        if not path.is_file():
            continue
        with Image.open(path) as source:
            art = source.convert("RGBA")
        if max(art.size) < MASTER:
            art = art.resize((MASTER, MASTER), Image.LANCZOS)
        out[stem] = art
    return out


def matches_png(image: Image.Image, path: Path) -> bool:
    """Whether PATH is on disk exactly as IMAGE would be saved."""
    if not path.is_file():
        return False
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return path.read_bytes() == buffer.getvalue()


def write_names(problems: list[str], write: bool) -> int:
    """Write every mapped place at every size, plus its scalable wrapper."""
    art = masters(set(PLACES.values()))
    written = 0
    for name, stem in sorted(PLACES.items()):
        image = art.get(stem)
        if image is None:
            problems.append(f"{PLACE_DIR.relative_to(ROOT)}/{stem}.png: missing "
                            f"for {name}")
            continue
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                target = folder / f"{name}.png"
                tile = resize(image, size * factor)
                if write:
                    folder.mkdir(parents=True, exist_ok=True)
                    save_png(tile, target)
                    written += 1
                elif not matches_png(tile, target):
                    problems.append(f"{target.relative_to(ROOT)}: not this artwork - "
                                    f"run make_theme_places.py")
        wrapper = SCALABLE / f"{name}.svg"
        text = svg_wrapper(image, name)
        if write:
            SCALABLE.mkdir(parents=True, exist_ok=True)
            save_text(text, wrapper)
            written += 1
        elif not wrapper.is_file() or wrapper.read_text() != text:
            problems.append(f"{wrapper.relative_to(ROOT)}: not this artwork - "
                            f"run make_theme_places.py")
    return written


def check_catalogue(problems: list[str]) -> None:
    """Every artwork stem used is catalogued, and every record is used."""
    records = catalogue()
    used = set(PLACES.values())
    for stem in sorted(used - set(records)):
        problems.append(f"library/places.json: {stem} is used but not catalogued")
    for stem in sorted(set(records) - used):
        problems.append(f"library/places.json: {stem} is catalogued but unused")
    for stem, record in sorted(records.items()):
        path = LIBRARY / record["file"]
        if not path.is_file():
            problems.append(f"{record['file']}: catalogued but missing")
            continue
        with Image.open(path) as image:
            if image.size != (record["native"], record["native"]):
                problems.append(f"{record['file']}: {image.size[0]} px, catalogue "
                                f"says {record['native']}")


def install(write: bool) -> tuple[int, list[str]]:
    problems: list[str] = []
    check_catalogue(problems)
    if any("is used but not catalogued" in problem for problem in problems):
        # Without a record the artwork is not cleared to ship; stop before it lands.
        return 0, problems
    return write_names(problems, write), problems


def check() -> list[str]:
    """Every mapped place in the theme, as ``library/places`` intends it."""
    problems: list[str] = []
    check_catalogue(problems)
    if any("used but not catalogued" in problem for problem in problems):
        return problems
    write_names(problems, write=False)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report drift instead of writing")
    args = parser.parse_args(argv)

    if args.check:
        problems = check()
        written = 0
    else:
        written, problems = install(True)

    if problems:
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        print(f"\n{len(problems)} place problem(s)", file=sys.stderr)
        return 1
    if args.check:
        print(f"ok: {len(PLACES)} place(s) match the era artwork in library/places")
    else:
        print(f"places: {len(PLACES)} name(s) dressed as the era drew them, "
              f"{written} file(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
