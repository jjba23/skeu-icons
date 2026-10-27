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

A few programs are shown under *another* icon instead of the object drawn for
them: the theme ships macOS artwork under its own names (``finder.png``,
``xcode.png``, ``terminal.png``), and those are what IntelliJ IDEA, Nautilus and
every terminal emulator answer with.  For those apps the names are pointed at
the borrowed artwork rather than at their own slug; the artwork itself is
committed in the theme, so this step mostly writes links.  ``BORROWED`` names
the individual trades (iMovie for a video editor, Disk Utility for a
partitioner), ``BORROWED_CATEGORIES`` the whole ones (every file manager is the
Finder, every game is Game Center), and ``BORROWED_NAMES`` covers programs no
desktop entry on this machine declares.

Two of those trades want the same object in a different colour - a second
editor should not be a pixel-for-pixel copy of the first program's tile - so
``ALTS`` cuts colourways out of committed artwork and writes them beside it at
every size.

    python3 tools/make_theme_apps.py            # install + link
    python3 tools/make_theme_apps.py --check    # report gaps, write nothing
"""

from __future__ import annotations

import argparse
import colorsys
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

#: Programs the pack shows under another icon than the one drawn for them, the
#: way a desktop dressed as OS X would dress them: iMovie for a video editor,
#: Disk Utility for a partitioner, Time Machine for a backup tool.  Keyed by app
#: slug, valued by a committed file stem in ``apps/``.
BORROWED: dict[str, str] = {
    "kdenlive": "imovie",              # a video editor, shown as iMovie
    "shotcut": "imovie",               # ... and so is the other open one
    "terminator": "terminal-red",      # the emulator that splits panes
    "totem": "quicktime-player",       # a film player, shown as QuickTime
    "celluloid": "quicktime-player",
    "ardour": "garageband",            # a DAW, shown as GarageBand
    "lmms": "garageband",
    "calendar": "ical",                # the tear-off desk calendar
    "joplin": "notes",                 # a notes app, shown as the OS X pad
    "document-viewer": "preview",      # a page viewer, shown as Preview
    "okular": "preview",
    "timeshift": "time-machine",       # a backup tool, shown as Time Machine
    "d-j-dup-backups": "time-machine",
    "gparted": "disk-utility",         # a partitioner, shown as Disk Utility
    "disks": "disk-utility",
    "settings": "system-preferences",  # the settings panel
    "gnome-system-monitor": "activity-monitor",
    "system-monitor": "activity-monitor",
    "software": "app-store",           # the package centre as the App Store
    "intellij-idea": "xcode",          # JetBrains' IDE, shown as the Xcode icon
}

#: Every terminal emulator answers with the pack's one terminal, so a machine
#: with six emulators installed still shows a single terminal icon.  That shared
#: artwork *is* the icon drawn for TERMINAL_SOURCE, so the two stay the same
#: picture whenever this step writes one of them.
TERMINAL_ART = "terminal"
TERMINAL_SOURCE = "console"

#: Categories whose applications answer with one Apple icon, because the
#: category *is* the Mac application: every file manager is the Finder, every
#: game is Game Center.  A slug in BORROWED always wins.
BORROWED_CATEGORIES: tuple[tuple[str, str], ...] = (
    ("TerminalEmulator", TERMINAL_ART),
    ("FileManager", "finder"),
    ("Game", "game-center"),
)

#: Programs in a mapped category that keep the object drawn for them: a game
#: store, an emulator or a Wine prefix is a shelf, not a game.
CATEGORY_KEEP: frozenset[str] = frozenset({
    "steam", "lutris", "heroic", "prism-launcher", "cartridges", "retroarch",
    "retrodeck", "retrodeck-configurator", "bottles", "wine",
})

#: Names a launcher asks for that no desktop entry on this machine declares - a
#: program that is only a menu alias, a dock's own button, a Wine export -
#: mapped straight to artwork.  ``tmux`` is not a terminal emulator and never
#: will be, but a launcher that starts it wants a terminal's tile.
BORROWED_NAMES: dict[str, str] = {
    "tmux": "terminal-red",
    "lightworks": "imovie-alt",
    "openshot": "imovie",
    "lambdock": "launchpad",
    "lambdock-launchpad": "launchpad",
    "org.jointhefreeworld.lambdock": "launchpad",
}

#: Colourways of borrowed artwork, written into the theme beside it so a second
#: program can have the same object in its own colours instead of a copy of the
#: first program's icon.  ``alt stem -> (source stem, hue, saturation, mode)``:
#: ``shift`` turns the artwork's own hues (a gold star becomes a red one and
#: keeps its shading), ``tint`` keeps its luminance and puts everything on one
#: hue, which is what turns graphite window chrome burgundy without taking the
#: white prompt with it.
ALTS: dict[str, tuple[str, float, float, str]] = {
    "imovie-alt": ("imovie", -52, 0.95, "shift"),
    "terminal-red": ("terminal", 356, 1.0, "tint"),
}

#: Names a launcher asks for when it wants "a terminal", not a named program.
GENERIC_TERMINAL_NAMES = ("utilities-terminal",)


def lookup_names(app: dict) -> list[str]:
    """Every name a shell or launcher may ask for, slug first."""
    names = [slugify(app["name"])]
    # Names declared by the roster (installed elsewhere) and the extra spellings
    # for hand-drawn artwork, before the ones this machine's entries declare.
    for value in (*app.get("names", []),):
        value = (value or "").strip()
        if value and value not in names:
            names.append(value)
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


def borrowed(app: dict) -> str:
    """The theme icon this app answers with, when it is not its own artwork."""
    slug = slugify(app["name"])
    if slug in BORROWED:
        return BORROWED[slug]
    categories = {name.strip() for name in (app.get("categories") or "").split(";")
                  if name.strip()}
    for category, art in BORROWED_CATEGORIES:
        if category in categories and slug not in CATEGORY_KEEP:
            return art
    return ""


def recoloured(image: Image.Image, hue: float, saturation: float,
               mode: str) -> Image.Image:
    """One artwork in another colourway (see ``ALTS``).

    ``shift`` turns every hue by HUE degrees, so a gold star becomes a red one
    and keeps its shading and its white parts; ``tint`` puts the whole picture
    on HUE while leaving light and dark where they are, so graphite chrome
    turns burgundy and a white prompt stays white.  Alpha is untouched: the
    colourway has the same shape as the artwork it came from.
    """
    source = image.convert("RGBA")
    data = source.tobytes()          # RGBA, four bytes per pixel, row by row
    pixels = []
    for index in range(0, len(data), 4):
        red, green, blue, alpha = data[index:index + 4]
        if not alpha:
            pixels.append((red, green, blue, alpha))
            continue
        current, lightness, sat = colorsys.rgb_to_hls(red / 255, green / 255, blue / 255)
        if mode == "tint":
            current = hue / 360.0
            sat = (1.0 - abs(2.0 * lightness - 1.0)) * saturation
        else:
            current = (current + hue / 360.0) % 1.0
            sat *= saturation
        painted = colorsys.hls_to_rgb(current, lightness, min(1.0, sat))
        pixels.append(tuple(round(channel * 255) for channel in painted) + (alpha,))
    out = Image.new("RGBA", source.size)
    out.putdata(pixels)
    return out


def write_alts(problems: list[str], write: bool) -> int:
    """Write every colourway in ``ALTS`` at every size; returns files written."""
    written = 0
    for stem, (source, hue, saturation, mode) in ALTS.items():
        master_path = THEME / "512x512@2x" / CONTEXT / f"{source}.png"
        if not master_path.is_file():
            problems.append(f"{master_path.relative_to(ROOT)}: missing for {stem}")
            continue
        with Image.open(master_path) as art:
            master = recoloured(art, hue, saturation, mode)
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                target = THEME / f"{size}x{size}{suffix}" / CONTEXT / f"{stem}.png"
                if write:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    resize(master, size * factor).save(target)
                    written += 1
                elif not target.is_file():
                    problems.append(f"{target.relative_to(ROOT)}: missing, expected "
                                    f"a colourway of {source}.png")
    return written


def refresh_terminal(problems: list[str], write: bool) -> int:
    """Keep ``terminal.png`` equal to the artwork drawn for TERMINAL_SOURCE."""
    source = ICONS / TERMINAL_SOURCE / "icon-1024.png"
    if not source.is_file():
        problems.append(f"{source.relative_to(ROOT)}: missing for {TERMINAL_ART}")
        return 0
    written = 0
    with Image.open(source) as drawn:
        master = drawn.convert("RGBA")
    for size in SIZES:
        for suffix, factor in (("", 1), ("@2x", 2)):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            if write:
                folder.mkdir(parents=True, exist_ok=True)
                resize(master, size * factor).save(folder / f"{TERMINAL_ART}.png")
                written += 1
            elif not (folder / f"{TERMINAL_ART}.png").is_file():
                problems.append(
                    f"{folder.relative_to(ROOT)}/{TERMINAL_ART}.png: missing")
    return written


def plan() -> list[tuple[str, list[str], bool, dict]]:
    """``[(slug, names, artwork_present, app), ...]`` for every discovered app."""
    out = []
    for app in discover():
        slug = slugify(app["name"])
        if not (ICONS / slug / "icon-1024.png").is_file():
            continue
        names = lookup_names(app)
        out.append((slug, names, (THEME / "48x48" / CONTEXT / f"{slug}.png").is_file(), app))
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
    for slug, names, _present, _app in plan():
        for name in names:
            table.setdefault(name, slug)
    return table


def link(path: Path, target: str, problems: list[str], write: bool,
         replace: bool = False) -> None:
    """Make PATH a relative symlink to TARGET (a sibling), without clobbering art.

    ``replace`` is set for the names of a borrowed icon: those have to move off
    the app's own artwork, so a real file in the way is the thing to replace.
    """
    if path.name == target:
        # The name *is* the artwork: a program mapped to its own icon, or the
        # borrowed file itself.  Nothing to point at.
        return
    if path.is_symlink():
        if os.readlink(path) == target:
            return
        if write:
            path.unlink()
        else:
            problems.append(f"{path.relative_to(ROOT)}: points at {os.readlink(path)}")
            return
    elif not path.exists():
        if not write:
            problems.append(f"{path.relative_to(ROOT)}: missing, expected a link "
                            f"to {target}")
            return
    else:
        if not replace:
            # A real file: hand-drawn artwork, or another app's icon. Never replace it.
            return
        if write:
            path.unlink()
        else:
            problems.append(f"{path.relative_to(ROOT)}: artwork, not a link to {target}")
            return
    if write:
        path.symlink_to(target)


def install(write: bool) -> tuple[int, int, list[str]]:
    problems: list[str] = []
    written = linked = 0
    owner = owners()
    apps = plan()

    # The shared terminal artwork is the icon drawn for the terminal archetype,
    # so keep it equal to TERMINAL_SOURCE's own drawing: one emulator's icon
    # changing means all of them change, instead of a stale committed copy
    # sitting under terminal.png for years.  This runs before the colourways
    # because terminal-red is cut from it.
    written += refresh_terminal(problems, write)
    written += write_alts(problems, write)

    for slug, names, present, app in apps:
        art = borrowed(app)
        master = None
        if not art:
            with Image.open(ICONS / slug / "icon-1024.png") as source:
                master = source.convert("RGBA")
        for size in SIZES:
            for suffix, factor in (("", 1), ("@2x", 2)):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                if art:
                    # The artwork is committed in the theme; only the names move.
                    icon = folder / f"{art}.png"
                    if not icon.is_file():
                        problems.append(f"{icon.relative_to(ROOT)}: missing for {slug}")
                        continue
                    # The app's own name always moves; a shared alias stays
                    # with the app that claimed it (see owners()).
                    wanted = [name for name in names
                              if name == slug or owner.get(name) == slug]
                else:
                    target = folder / f"{slug}.png"
                    if not target.exists() or not present:
                        if write:
                            folder.mkdir(parents=True, exist_ok=True)
                            resize(master, size * factor).save(target)
                            written += 1
                        else:
                            problems.append(f"{target.relative_to(ROOT)}: missing")
                    wanted = [alias for alias in names[1:] if owner.get(alias) == slug]
                for name in wanted:
                    alias_path = folder / f"{name}.png"
                    before = alias_path.is_symlink() or alias_path.exists()
                    link(alias_path, f"{art or slug}.png", problems, write, replace=bool(art))
                    if write and not before:
                        linked += 1

    # "a terminal" is a name a launcher asks for without naming any program.
    for size in SIZES:
        for suffix in ("", "@2x"):
            folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
            if not (folder / f"{TERMINAL_ART}.png").is_file():
                continue
            for name in GENERIC_TERMINAL_NAMES:
                if owner.get(name):
                    continue
                path = folder / f"{name}.png"
                before = path.is_symlink() or path.exists()
                link(path, f"{TERMINAL_ART}.png", problems, write)
                if write and not before:
                    linked += 1

    # Programs no desktop entry here declares: a menu alias, a dock's own
    # button, a Wine export.  They answer with the artwork they are mapped to,
    # so a launcher that names them gets a tile instead of a generic gear.
    for name, art in sorted(BORROWED_NAMES.items()):
        for size in SIZES:
            for suffix in ("", "@2x"):
                folder = THEME / f"{size}x{size}{suffix}" / CONTEXT
                if not (folder / f"{art}.png").is_file():
                    continue
                path = folder / f"{name}.png"
                before = path.is_symlink() or path.exists()
                link(path, f"{art}.png", problems, write, replace=True)
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
    aliases = sum(len(names) - 1 for _slug, names, _present, _app in apps)

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
