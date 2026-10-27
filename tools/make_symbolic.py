#!/usr/bin/env python3
"""Draw the symbolic layer: one Aqua glyph for every Adwaita symbolic name.

The parity contract lives in ``tools/symbolic-names.txt``, copied from the
``symbolic/`` tree of the installed Adwaita theme.  Each line is
``<context>/<name>``; this programme folds the ``-symbolic`` suffix and the two
``-rtl`` spellings back to a base name, looks the base up in
:mod:`skeu.aqua_catalog`, mirrors the artwork when the name asks for it, and
writes ``skeu-icons/symbolic/<context>/<name>.svg``.

    python3 tools/make_symbolic.py               # all 646 icons
    python3 tools/make_symbolic.py --only actions
    python3 tools/make_symbolic.py --ink dark    # light ink, for the dark theme
    python3 tools/make_symbolic.py --sheet       # proof sheet in /tmp/skeu
    python3 tools/make_symbolic.py --check       # nothing stale, nothing missing

Exit status is 1 when a name has no glyph, when the theme has a file the contract
does not list, or when a file on disk differs from what the catalogue produces.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from skeu import aqua  # noqa: E402
from skeu.aqua_catalog import SYMBOLIC  # noqa: E402

THEME = ROOT / "skeu-icons"
OUT = THEME / "symbolic"
CONTRACT = Path(__file__).resolve().parent / "symbolic-names.txt"

#: How close to the tile edge ink may come, in grid units.  The pack's own
#: envelope is 0.94..15.06 (a folder's stroke), so this is the margin the
#: artwork is drawn to rather than a tightening of it.
MARGIN = 0.9

#: How far the traced outline may sit from the paint it came from, in grid
#: units.  Tracing follows pixel corners and simplifies the staircase within
#: ``aqua.SMOOTH`` raster pixels, so a couple of those is the whole allowance.
TRACE_DRIFT = 3 / aqua.RASTER

INK = {"light": aqua.INK_LIGHT, "dark": aqua.INK_DARK}


def read_contract() -> list[tuple[str, str]]:
    """``[(context, name), ...]`` from the parity file, comments skipped."""
    names = []
    for line in CONTRACT.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        context, _, name = line.partition("/")
        if not name:
            raise SystemExit(f"{CONTRACT.name}: {line!r} is not <context>/<name>")
        names.append((context, name))
    return names


def base_name(name: str) -> tuple[str, bool]:
    """``(base, mirrored)`` for a full symbolic file name."""
    base = re.sub(r"-symbolic$", "", name)
    mirrored = base.endswith("-rtl")
    if mirrored:
        base = base[:-4]
    base = re.sub(r"-symbolic$", "", base)
    return base, mirrored


def render(context: str, name: str, ink: str = "light",
           title: str | None = None) -> str:
    """The SVG text for one name; raises KeyError if it has no glyph."""
    base, mirrored = base_name(name)
    try:
        glyph_fn, kwargs = SYMBOLIC[base]
    except KeyError:
        raise KeyError(f"{context}/{name}: no glyph for {base!r}") from None
    glyph = aqua.Glyph()
    glyph_fn(glyph, **kwargs)
    glyph.mirror = mirrored
    return glyph.svg(ink=INK[ink], title=title if title is not None else name)


def plan(only: str | None = None) -> list[tuple[str, str, Path]]:
    items = []
    for context, name in read_contract():
        if only and context != only:
            continue
        items.append((context, name, OUT / context / f"{name}.svg"))
    return items


def build(only: str | None = None, ink: str = "light", quiet: bool = False) -> int:
    missing: list[str] = []
    written = 0
    for context, name, path in plan(only):
        try:
            text = render(context, name, ink)
        except KeyError as error:
            missing.append(str(error).strip("'\""))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_text() != text:
            path.write_text(text)
            written += 1
    if missing:
        for problem in missing:
            print(f"  no glyph: {problem}", file=sys.stderr)
        print(f"\n{len(missing)} name(s) have no glyph in skeu/aqua_catalog.py",
              file=sys.stderr)
        return 1
    if not quiet:
        total = len(plan(only))
        print(f"symbolic: {total} name(s), {written} written -> {OUT}")
    return 0


def check(only: str | None = None, ink: str = "light") -> list[str]:
    """Problems with what is on disk, as sentences."""
    problems: list[str] = []
    expected = plan(only)
    for context, name, path in expected:
        if not path.is_file():
            problems.append(f"{path.relative_to(ROOT)}: missing")
            continue
        try:
            text = render(context, name, ink)
        except KeyError as error:
            problems.append(str(error).strip("'\""))
            continue
        if path.read_text() != text:
            problems.append(f"{path.relative_to(ROOT)}: stale - run make_symbolic.py")
    listed = {path for _context, _name, path in expected}
    for path in sorted(OUT.rglob("*.svg")):
        if path not in listed:
            problems.append(f"{path.relative_to(ROOT)}: not in the parity contract")
    return problems


def outline_bounds(loops: list[list[tuple[float, float]]]):
    """``(left, top, right, bottom)`` of traced contours, or None if empty."""
    xs = [x for loop in loops for x, _y in loop]
    ys = [y for loop in loops for _x, y in loop]
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def audit() -> list[str]:
    """Problems you can only see by looking: blanks, clipped and jammed drawings.

    ``--check`` compares files to the catalogue, so a glyph that draws nothing,
    one whose ink runs off the 16 px tile, or one that stops a twentieth of a
    pixel short of the edge passes it happily.  All three read as "the icon is
    broken" on screen - the last one because the stroke is anti-aliased into
    the boundary and looks cut - so they are checked here instead.

    The traced outline is also measured against the paint it came from: the
    shipped path must occupy the same box as the mask.  ``--check`` cannot see
    a tracer that reads a bitmap's rows as columns, because both sides of the
    comparison run through the tracer; every icon comes out a quarter turn
    left and the ``.svg`` files still agree with the catalogue.
    """
    import numpy as np

    problems: list[str] = []
    for base, (glyph_fn, kwargs) in sorted(SYMBOLIC.items()):
        glyph = aqua.Glyph()
        glyph_fn(glyph, **kwargs)
        ink = np.asarray(glyph.mask()) > 127
        rows, columns = np.nonzero(ink)
        if not len(rows):
            problems.append(f"{base}: draws nothing")
            continue
        top, left = rows.min() / aqua.RASTER, columns.min() / aqua.RASTER
        bottom = (rows.max() + 1) / aqua.RASTER
        right = (columns.max() + 1) / aqua.RASTER
        if min(top, left) < MARGIN or max(bottom, right) > 16 - MARGIN:
            problems.append(f"{base}: ink {left:.2f}..{right:.2f} x {top:.2f}.."
                            f"{bottom:.2f} crowds the tile edge "
                            f"(keep inside {MARGIN}..{16 - MARGIN:g})")
        outline = outline_bounds(glyph.contours())
        if outline is None:
            problems.append(f"{base}: paints ink but traces to no path")
            continue
        drift = max(abs(outline[i] - painted) for i, painted in
                    enumerate((left, top, right, bottom)))
        if drift > TRACE_DRIFT:
            problems.append(f"{base}: traced path {outline[0]:.2f}..{outline[2]:.2f}"
                            f" x {outline[1]:.2f}..{outline[3]:.2f} does not match "
                            f"the paint {left:.2f}..{right:.2f} x {top:.2f}.."
                            f"{bottom:.2f} (off by {drift:.2f}, allowed "
                            f"{TRACE_DRIFT:.2f})")
    return problems


def sheet(target: Path, columns: int = 32, cell: int = 40) -> Path:
    """A PNG proof sheet of every glyph, rendered by one Inkscape call."""
    items = plan()
    rows = (len(items) + columns - 1) // columns
    width, height = columns * cell, rows * cell
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             f'<rect width="{width}" height="{height}" fill="#f6f5f4"/>']
    for index, (_context, name, path) in enumerate(items):
        x = (index % columns) * cell + 4
        y = (index // columns) * cell + 4
        parts.append(f'<rect x="{x - 2}" y="{y - 2}" width="{cell - 4}" '
                     f'height="{cell - 4}" fill="none" stroke="#ddd9d6"/>')
        parts.append(f'<image x="{x}" y="{y}" width="{cell - 8}" height="{cell - 8}" '
                     f'xlink:href="{path.as_uri()}"/>')
    parts.append("</svg>")
    source = target.with_suffix(".svg")
    source.write_text("\n".join(parts))
    inkscape = shutil.which("inkscape")
    if not inkscape:
        print(f"wrote {source} (inkscape not found, no PNG)")
        return source
    subprocess.run([inkscape, str(source), "--export-type=png",
                    f"--export-filename={target}"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {target} ({len(items)} icons, {columns} per row)")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", choices=("actions", "categories", "devices",
                                           "emotes", "legacy", "mimetypes",
                                           "places", "status", "ui"),
                        help="render one context")
    parser.add_argument("--ink", choices=("light", "dark"), default="light",
                        help="ink colour of the shipped SVG (default: light)")
    parser.add_argument("--check", action="store_true",
                        help="do not write; fail if anything is missing or stale")
    parser.add_argument("--audit", action="store_true",
                        help="report glyphs that draw nothing, run off the tile, "
                             "or whose traced path does not match the paint")
    parser.add_argument("--sheet", nargs="?", const="/tmp/skeu/symbolic.png",
                        metavar="PNG", help="write a proof sheet")
    args = parser.parse_args(argv)

    if args.sheet:
        sheet(Path(args.sheet))
        return 0
    if args.audit:
        problems = audit()
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} glyph(s) need a look", file=sys.stderr)
            return 1
        print(f"ok: {len(SYMBOLIC)} glyphs are painted inside the "
              f"{MARGIN}..{16 - MARGIN:g} margin and trace back to the same box")
        return 0
    if args.check:
        problems = check(args.only, args.ink)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) found", file=sys.stderr)
            return 1
        print(f"ok: {len(plan(args.only))} symbolic icons match the catalogue")
        return 0
    return build(args.only, args.ink)


if __name__ == "__main__":
    sys.exit(main())
