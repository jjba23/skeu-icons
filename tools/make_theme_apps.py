#!/usr/bin/env python3
"""Put the drawn app icons into the theme under every name a desktop asks for.

``make_app_icons.py`` draws one icon per installed program and files it under a
slug (``app-icons/wezterm/``).  A desktop never asks for that slug: it asks for
whatever the program wrote in its desktop entry - ``org.wezfurlong.wezterm``, or
the desktop id ``com.usebruno.Bruno``, or the window class.  Without those
spellings the icon is simply not found and the toolkit falls through to
Adwaita.

This step closes that gap: it copies any app icon the theme is missing into
``skeu-icons/<size>x<size>/apps/`` and links every name the entries declare to
the artwork.  Existing artwork is never overwritten - the pack's hand-drawn
Emacs and calculator keep their place, and only the links are added.

    python3 tools/make_theme_apps.py            # install + link
    python3 tools/make_theme_apps.py --check    # report gaps, write nothing
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_app_icons import discover  # noqa: E402
from render_skeu import resize, slugify  # noqa: E402

THEME = ROOT / "skeu-icons"
ICONS = ROOT / "app-icons"

#: The sizes the theme ships as bitmaps; every alias is mirrored into ``@2x``.
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "apps"


def lookup_names(app: dict) -> list[str]:
    """Every name a shell or launcher may ask for, slug first."""
    names = [slugify(app["name"])]
    for value in (app.get("icon", ""), app.get("wmclass", ""),
                  *app.get("desktops", [])):
        value = (value or "").strip()
        if not value:
            continue
        # A desktop entry may point straight at a file; that is not a name.
        if "/" in value or value.startswith(".") or re.search(r"\.(png|svg|xpm)$", value):
            continue
        if value not in names:
            names.append(value)
    return names


def plan() -> list[tuple[str, list[str], bool]]:
    """``[(slug, aliases, artwork_present), ...]`` for every discovered app."""
    out = []
    for app in discover():
        slug = slugify(app["name"])
        if not (ICONS / slug / "icon-1024.png").is_file():
            continue
        names = lookup_names(app)
        out.append((slug, names, (THEME / "48x48" / CONTEXT / f"{slug}.png").is_file()))
    return out


def owners() -> dict[str, str]:
    """``{lookup name: slug}``, first claimant wins.

    Two programs can declare the same name - ``Emacs`` and ``Emacs (Client)``
    both answer to ``emacs``, Wireshark and its super-user mode to
    ``org.wireshark.Wireshark``.  Only one icon can sit under a name, so the
    first app in catalogue order keeps it and the later ones leave it alone;
    otherwise the last app processed would silently steal it from the first
    and the check would disagree with the build.
    """
    table: dict[str, str] = {}
    for slug, names, _present in plan():
        for name in names:
            table.setdefault(name, slug)
    return table


def link(path: Path, target: str, problems: list[str], write: bool) -> None:
    """Make PATH a relative symlink to TARGET (a sibling), without clobbering art."""
    if path.is_symlink():
        if os.readlink(path) == target:
            return
        if write:
            path.unlink()
        else:
            problems.append(f"{path.relative_to(ROOT)}: points at {os.readlink(path)}")
            return
    elif path.exists():
        # A real file: hand-drawn artwork, or another app's icon. Never replace it.
        return
    if write:
        path.symlink_to(target)


def install(write: bool) -> tuple[int, int, list[str]]:
    problems: list[str] = []
    written = linked = 0
    owner = owners()
    for slug, names, present in plan():
        with Image.open(ICONS / slug / "icon-1024.png") as source:
            master = source.convert("RGBA")
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                target = folder / f"{slug}.png"
                if not target.exists() or not present:
                    if write:
                        folder.mkdir(parents=True, exist_ok=True)
                        resize(master, size * factor).save(target)
                        written += 1
                    else:
                        problems.append(f"{target.relative_to(ROOT)}: missing")
                for alias in names[1:]:
                    if owner.get(alias) != slug:
                        continue
                    alias_path = folder / f"{alias}.png"
                    before = alias_path.is_symlink() or alias_path.exists()
                    link(alias_path, f"{slug}.png", problems, write)
                    if write and not before:
                        linked += 1
    return written, linked, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="report what is missing instead of writing")
    args = parser.parse_args(argv)

    write = not args.check
    written, linked, problems = install(write)
    apps = plan()
    aliases = sum(len(names) - 1 for _slug, names, _present in apps)

    if problems:
        for problem in problems[:40]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 40:
            print(f"  ... and {len(problems) - 40} more", file=sys.stderr)
        print(f"\n{len(problems)} app icon problem(s)", file=sys.stderr)
        return 1
    if write:
        print(f"apps: {len(apps)} icon(s), {written} bitmap(s), "
              f"{aliases} alias name(s) in the theme")
    else:
        print(f"ok: {len(apps)} app icon(s) and {aliases} alias name(s) are in the theme")
    return 0


if __name__ == "__main__":
    sys.exit(main())
