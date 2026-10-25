#!/usr/bin/env python3
"""Build the accent and lightness variants as symlink themes.

``skeu-icons`` carries coloured folder artwork for every accent in the palette
(``folder-orange.png``, ``folder-pink-desktop.png``, ...) but only one of them is
the default.  A variant picks an accent by *pointing the neutral names at that
artwork*, and it does it with relative symlinks, so a variant theme costs a few
hundred links instead of another copy of the bitmaps:

    skeu-icons-orange/48x48/places/folder.png
        -> ../../../skeu-icons/48x48/places/folder-orange.png

Everything a variant does not override is reached through ``Inherits=skeu-icons``
in its ``index.theme``, which is how ``Adwaita-dark`` works.  So there is one
theme per accent, plus a ``-dark`` sibling for each:

    skeu-icons-<accent>        that accent on the neutral materials
    skeu-icons-<accent>-dark   same artwork, light-ink symbolic icons

A symbol is recoloured by the toolkit, but a file manager, a Qt app or anything
that renders a ``-symbolic`` SVG as plain artwork needs the ink to match the
background.  The light-ink set lives once, in ``skeu-icons-dark``, and every
``-dark`` variant reaches it through a single relative directory symlink
(``symbolic -> ../skeu-icons-dark/symbolic``) instead of shipping fourteen copies
of the same 646 files.

    python3 tools/make_variants.py             # rewrite every variant theme
    python3 tools/make_variants.py --check     # verify what is on disk

Relative links mean the trees keep working after ``install.sh`` copies them:
every theme lives in the same parent directory, in the pack and in
``~/.local/share/icons``.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from make_symbolic import read_contract, render  # noqa: E402

BASE_DIR = "skeu-icons"
BASE = ROOT / BASE_DIR
DARK_DIR = "skeu-icons-dark"

SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "Places"

#: The accent palette the pack ships folder artwork for.
ACCENTS = ("red", "orange", "yellow", "lime", "green", "teal", "cyan", "blue",
           "indigo", "violet", "magenta", "pink", "brown", "graphite")

SYMBOLIC_CONTEXT = {"actions": "Actions", "categories": "Categories",
                    "devices": "Devices", "emotes": "Emotes", "legacy": "Legacy",
                    "mimetypes": "MimeTypes", "places": "Places",
                    "status": "Status", "ui": "UI"}

HEADER = """[Icon Theme]
Name={name}
Comment={comment}
Example=folder
Inherits={inherits}
DisplayDepth=32
LinkOverlay=emblem-symbolic-link
LockOverlay=emblem-readonly

# No freedesktop key marks a theme as dark: desktops and libadwaita pick it by
# name or by the icon-theme setting, so the name is the contract.  Everything
# this theme does not override resolves through Inherits=, which keeps the
# variant a few hundred symlinks instead of a second copy of the artwork.
"""


def accent_overrides(accent: str) -> list[tuple[str, str]]:
    """``[(variant relative path, base relative path)]`` for the accent artwork.

    A neutral name is overridden only when the pack actually ships that accent
    for it, so a variant never invents artwork that does not exist.
    """
    links: list[tuple[str, str]] = []
    for size in SIZES:
        for suffix in ("", "@2x"):
            folder = f"{size}x{size}{suffix}/{CONTEXT.lower()}"
            directory = BASE / folder
            if not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                stem = path.stem
                if not stem.startswith("folder") or f"-{accent}-" in stem or \
                        stem.endswith(f"-{accent}"):
                    continue
                if stem == "folder":
                    coloured = f"folder-{accent}{path.suffix}"
                else:
                    rest = stem[len("folder-"):]
                    coloured = f"folder-{accent}-{rest}{path.suffix}"
                if (directory / coloured).is_file():
                    links.append((f"{folder}/{path.name}",
                                  f"{BASE_DIR}/{folder}/{coloured}"))
    return links


def path_sections(dirs: list[str], scaled: list[str]) -> str:
    """The ``[dir]`` sections for an index.theme."""
    blocks = []
    for name in dirs:
        if name.startswith("symbolic/"):
            context = SYMBOLIC_CONTEXT[name.split("/", 1)[1]]
            blocks.append(f"[{name}]\nSize=16\nMinSize=8\nMaxSize=512\n"
                          f"Context={context}\nType=Scalable\n")
            continue
        size = int(name.split("x")[0])
        blocks.append(f"[{name}]\nSize={size}\nContext={CONTEXT}\nType=Fixed\n")
    for name in scaled:
        size = int(name.split("x")[0])
        blocks.append(f"[{name}]\nSize={size}\nScale=2\nContext={CONTEXT}\n"
                      f"Type=Fixed\n")
    return "\n".join(blocks)


def variant_names() -> list[tuple[str, str, str, str | None, bool]]:
    """``[(directory, display name, comment, accent, dark)]`` for every variant."""
    names = [(DARK_DIR, "Skeu Icons Dark",
              "Skeuomorphic icons with light-ink symbolic icons for dark desktops",
              None, True)]
    for accent in ACCENTS:
        title = accent.title()
        names.append((f"{BASE_DIR}-{accent}", f"Skeu Icons {title}",
                      f"Skeuomorphic icons: {accent} enamel accent on the neutral "
                      f"materials", accent, False))
        names.append((f"{BASE_DIR}-{accent}-dark", f"Skeu Icons {title} Dark",
                      f"Skeuomorphic icons: {accent} accent, light symbolic ink "
                      f"for dark desktops", accent, True))
    return names


def order(name: str) -> tuple:
    """Raster dirs by size, then the symbolic contexts by name."""
    if name.startswith("symbolic/"):
        return (1, 0, name)
    return (0, int(name.split("x")[0]), name)


def write_index(target: Path, name: str, comment: str, inherits: str,
                heavy: list[str], scaled: list[str]) -> None:
    header = HEADER.format(name=name, comment=comment, inherits=inherits)
    body = []
    if heavy:
        body.append("Directories=" + ",".join(heavy))
    if scaled:
        body.append("ScaledDirectories=" + ",".join(scaled))
    index = header + "\n".join(body) + "\n\n" + path_sections(heavy, scaled)
    (target / "index.theme").write_text(index + "\n")


def symbolic_entries() -> list[str]:
    """``symbolic/<context>`` for every context in the parity contract."""
    entries: list[str] = []
    for context, _name in read_contract():
        entry = f"symbolic/{context}"
        if entry not in entries:
            entries.append(entry)
    return sorted(entries, key=order)


def build_dark() -> int:
    """The shared theme: base artwork plus a light-ink copy of every symbol."""
    target = ROOT / DARK_DIR
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    written = 0
    for context, name in read_contract():
        out = target / "symbolic" / context / f"{name}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(context, name, ink="dark"))
        written += 1
    write_index(target, "Skeu Icons Dark",
                "Skeuomorphic icons with light-ink symbolic icons for dark desktops",
                f"{BASE_DIR},AdwaitaLegacy,hicolor", symbolic_entries(), [])
    return written


def build_accent(directory: str, name: str, comment: str, accent: str,
                 dark: bool) -> tuple[int, int]:
    """(symlinks, symbolic links) for one accent variant; the directory is rewritten."""
    target = ROOT / directory
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()

    links = accent_overrides(accent)
    for relative, destination in links:
        link = target / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(ROOT / destination, link.parent))

    symbolic = 0
    if dark:
        # One relative directory link reaches the shared light-ink layer, which
        # install.sh copies beside this theme.
        target.joinpath("symbolic").symlink_to(os.path.join("..", DARK_DIR, "symbolic"))
        symbolic = len(list(read_contract()))

    dirs = sorted({str(Path(relative).parent) for relative, _d in links}, key=order)
    scaled = [d for d in dirs if "@2x" in d]
    heavy = [d for d in dirs if "@2x" not in d]
    if dark:
        heavy = sorted(set(heavy) | set(symbolic_entries()), key=order)

    inherits = [BASE_DIR]
    if dark:
        inherits = [DARK_DIR, BASE_DIR]
    write_index(target, name, comment, ",".join(inherits + ["AdwaitaLegacy", "hicolor"]),
                heavy, scaled)
    return len(links), symbolic


def build(quiet: bool = False) -> int:
    symbolic = build_dark()
    if not quiet:
        print(f"{DARK_DIR}: {symbolic} light-ink symbolic files")
    for directory, name, comment, accent, dark in variant_names():
        if accent is None:
            continue
        links, symbolic_links = build_accent(directory, name, comment, accent, dark)
        if not quiet:
            detail = f"{links} symlinks"
            if symbolic_links:
                detail += f", {symbolic_links} symbolic icons via {DARK_DIR}"
            print(f"{directory}: {detail}")
    return 0


def check() -> list[str]:
    """Problems with the variant trees on disk, as sentences."""
    problems: list[str] = []
    for directory, name, _comment, accent, dark in variant_names():
        target = ROOT / directory
        index = target / "index.theme"
        if not index.is_file():
            problems.append(f"{directory}/index.theme: missing - run make_variants.py")
            continue
        text = index.read_text()
        if f"Name={name}" not in text:
            problems.append(f"{directory}/index.theme: Name= is not {name!r}")
        expected_links = {r for r, _d in accent_overrides(accent)} if accent else set()
        present = {str(p.relative_to(target)) for p in target.rglob("*")
                   if p.is_symlink() and p.name != "symbolic"}
        for want in sorted(expected_links - present):
            problems.append(f"{directory}/{want}: accent symlink missing")
        for extra in sorted(present - expected_links):
            problems.append(f"{directory}/{extra}: symlink not in the accent map")
        for link in target.rglob("*"):
            if link.is_symlink() and not link.exists():
                problems.append(f"{directory}/{link.relative_to(target)}: "
                                f"dangling -> {os.readlink(link)}")
        if dark:
            symbolic = target / "symbolic"
            if not symbolic.is_dir():
                problems.append(f"{directory}/symbolic: missing light-ink layer")
        declared = set()
        for line in text.splitlines():
            if line.startswith(("Directories=", "ScaledDirectories=")):
                declared |= {d for d in line.split("=", 1)[1].split(",") if d}
        for entry in sorted(declared):
            if not (target / entry).is_dir():
                problems.append(f"{directory}/{entry}: declared but missing")
        for entry in sorted({str(p.parent.relative_to(target))
                             for p in target.rglob("*") if p.is_file()
                             and p.name != "index.theme"}):
            if entry not in declared:
                problems.append(f"{directory}/{entry}: holds icons but is not "
                                f"declared in index.theme")
    dark_target = ROOT / DARK_DIR
    if dark_target.is_dir():
        expected = {f"symbolic/{c}/{n}.svg" for c, n in read_contract()}
        present = {str(p.relative_to(dark_target)) for p in dark_target.rglob("*.svg")}
        missing = expected - present
        if missing:
            problems.append(f"{DARK_DIR}: {len(missing)} light-ink symbolic file(s) "
                            f"missing (e.g. {sorted(missing)[0]})")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="verify the variants on disk instead of writing them")
    args = parser.parse_args(argv)
    if args.check:
        problems = check()
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) found", file=sys.stderr)
            return 1
        print(f"ok: {len(ACCENTS)} accent themes + their dark siblings match "
              f"their accent maps")
        return 0
    return build()


if __name__ == "__main__":
    sys.exit(main())
