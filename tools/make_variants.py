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

A variant also *mirrors* the base theme's coloured context trees - ``apps``,
``mimetypes``, ``devices``, ``emblems``, ``categories`` and the ``scalable``
trees - as one relative directory symlink each (``48x48/mimetypes ->
../../skeu-icons/48x48/mimetypes``).  Without them a variant would ship the
symbolic layer alone, and that is enough to shadow the artwork: a toolkit is
handed a chain like ``image-jpeg, image-x-generic, image-jpeg-symbolic,
image-x-generic-symbolic``, it walks ``Inherits=`` only after a name fails in
the theme itself, and a name's ``-symbolic`` twin counts as a hit.  So the
variant's ``image-x-generic-symbolic`` answered before the chain ever reached
``skeu-icons/48x48/mimetypes/image-jpeg.png``, and every image, archive,
document, audio file and video drew the same handful of monochrome glyphs.
Mirroring the coloured trees makes the plain name resolve inside the variant,
where it wins over the symbolic twin exactly as it does in the base theme.

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
SYMBOLIC_DIR = "symbolic"

SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXT = "Places"

#: The accent palette the pack ships folder artwork for.
ACCENTS = ("red", "orange", "yellow", "lime", "green", "teal", "cyan", "blue",
           "indigo", "violet", "magenta", "pink", "brown", "graphite")

SYMBOLIC_CONTEXT = {"actions": "Actions", "categories": "Categories",
                    "devices": "Devices", "emotes": "Emotes", "legacy": "Legacy",
                    "mimetypes": "MimeTypes", "places": "Places",
                    "status": "Status", "ui": "UI"}

#: The one coloured tree an accent variant must not mirror.  It owns the folder
#: artwork, and the base theme's ``scalable/places/folder.svg`` is the neutral
#: one: mirroring it lets a 96 px lookup pick the neutral SVG over the accent's
#: own ``128x128@2x/places/folder.png``, and the folders lose their enamel.
ACCENT_SKIP = {"scalable/places"}

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


def neutral_places_links() -> list[tuple[str, str]]:
    """``[(variant relative path, base relative path)]`` for the non-folder places.

    The accent map owns every ``folder`` name, so the handful of places the pack
    also draws - ``user-home``, ``user-desktop``, ``user-bookmarks``,
    ``inode-directory`` - have to be mirrored into the variant's own places
    directories.  Leaving them to ``Inherits=`` lets their ``-symbolic`` twins
    answer first, which is how ``application/x.systemd-home`` ended up drawing
    the monochrome home glyph.
    """
    links: list[tuple[str, str]] = []
    for size in SIZES:
        for suffix in ("", "@2x"):
            folder = f"{size}x{size}{suffix}/{CONTEXT.lower()}"
            directory = BASE / folder
            if not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                if path.stem.startswith("folder"):
                    continue
                links.append((f"{folder}/{path.name}",
                              f"{BASE_DIR}/{folder}/{path.name}"))
    return links


def variant_links(accent: str) -> list[tuple[str, str]]:
    """Every file a variant places itself: the accent tree plus the neutral places."""
    return accent_overrides(accent) + neutral_places_links()


def base_sections() -> tuple[list[str], list[str], dict[str, str]]:
    """The base theme's declared directories and their ``[section]`` bodies.

    A mirrored directory keeps the base theme's own ``Size``/``Context``/``Type``
    lines verbatim instead of guessing them from the directory name, so
    ``scalable/mimetypes`` stays ``Scalable`` and ``48x48@2x/apps`` keeps its
    ``Scale=2``.
    """
    direct: list[str] = []
    scaled: list[str] = []
    bodies: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for raw in (BASE / "index.theme").read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            if current:
                bodies[current] = "\n".join(lines)
            current = line[1:-1]
            lines = []
            continue
        if line.startswith("Directories="):
            direct = [entry for entry in line.split("=", 1)[1].split(",") if entry]
            continue
        if line.startswith("ScaledDirectories="):
            scaled = [entry for entry in line.split("=", 1)[1].split(",") if entry]
            continue
        if current:
            lines.append(line)
    if current:
        bodies[current] = "\n".join(lines)
    bodies.pop("Icon Theme", None)
    return direct, scaled, bodies


def inherited_dirs() -> list[str]:
    """The base theme's coloured directories, which every variant mirrors.

    ``symbolic/`` is left out: the light theme already inherits it from the base
    theme, and the ``-dark`` variants point at the shared light-ink copy.
    """
    direct, scaled, _bodies = base_sections()
    return [entry for entry in direct + scaled
            if not entry.startswith(f"{SYMBOLIC_DIR}/")]


def path_sections(dirs: list[str], scaled: list[str],
                  bodies: dict[str, str]) -> str:
    """The ``[dir]`` sections for an index.theme."""
    blocks = []
    for name in dirs + scaled:
        if name in bodies:
            blocks.append(f"[{name}]\n{bodies[name]}\n")
            continue
        if name.startswith("symbolic/"):
            context = SYMBOLIC_CONTEXT[name.split("/", 1)[1]]
            blocks.append(f"[{name}]\nSize=16\nMinSize=8\nMaxSize=512\n"
                          f"Context={context}\nType=Scalable\n")
            continue
        size = int(name.split("x")[0])
        if "@2x" in name:
            blocks.append(f"[{name}]\nSize={size}\nScale=2\nContext={CONTEXT}\n"
                          f"Type=Fixed\n")
            continue
        blocks.append(f"[{name}]\nSize={size}\nContext={CONTEXT}\nType=Fixed\n")
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
    """Raster dirs by size, then the scalable and symbolic contexts by name."""
    if name.startswith(("symbolic/", "scalable/")):
        return (1, 0, name)
    return (0, int(name.split("x")[0]), name)


def write_index(target: Path, name: str, comment: str, inherits: str,
                heavy: list[str], scaled: list[str],
                bodies: dict[str, str]) -> None:
    header = HEADER.format(name=name, comment=comment, inherits=inherits)
    body = []
    if heavy:
        body.append("Directories=" + ",".join(heavy))
    if scaled:
        body.append("ScaledDirectories=" + ",".join(scaled))
    index = (header + "\n".join(body) + "\n\n"
             + path_sections(heavy, scaled, bodies))
    (target / "index.theme").write_text(index + "\n")


def symbolic_entries() -> list[str]:
    """``symbolic/<context>`` for every context in the parity contract."""
    entries: list[str] = []
    for context, _name in read_contract():
        entry = f"symbolic/{context}"
        if entry not in entries:
            entries.append(entry)
    return sorted(entries, key=order)


def mirror_coloured(target: Path, skip: set[str] | None = None) -> list[str]:
    """Link the base theme's coloured trees into TARGET; return what was linked.

    The accent variants create their own ``places`` trees first, so an existing
    directory is left alone and only the missing contexts are mirrored.
    """
    skipped = skip or set()
    mirrored: list[str] = []
    for entry in inherited_dirs():
        if entry in skipped:
            continue
        link = target / entry
        if link.is_symlink() or link.exists():
            continue
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(BASE / entry, link.parent))
        mirrored.append(entry)
    return mirrored


def build_dark() -> tuple[int, int]:
    """The shared theme: base artwork plus a light-ink copy of every symbol."""
    target = ROOT / DARK_DIR
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()
    written = 0
    for context, name in read_contract():
        out = target / SYMBOLIC_DIR / context / f"{name}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(context, name, ink="dark"))
        written += 1
    mirrored = mirror_coloured(target)
    heavy = sorted(set(mirrored) - {d for d in mirrored if "@2x" in d}
                   | set(symbolic_entries()), key=order)
    scaled = sorted({d for d in mirrored if "@2x" in d}, key=order)
    write_index(target, "Skeu Icons Dark",
                "Skeuomorphic icons with light-ink symbolic icons for dark desktops",
                f"{BASE_DIR},AdwaitaLegacy,hicolor", heavy, scaled,
                base_sections()[2])
    return written, len(mirrored)


def build_accent(directory: str, name: str, comment: str, accent: str,
                 dark: bool) -> tuple[int, int, int]:
    """(accent links, coloured dirs mirrored, symbolic links) for one variant."""
    target = ROOT / directory
    if target.exists():
        shutil.rmtree(target)
    target.mkdir()

    links = variant_links(accent)
    for relative, destination in links:
        link = target / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(ROOT / destination, link.parent))

    # The accent owns the places trees; everything else the pack draws is
    # mirrored so the plain name resolves here, ahead of any symbolic twin.
    mirrored = mirror_coloured(target, skip=ACCENT_SKIP)

    symbolic = 0
    if dark:
        # One relative directory link reaches the shared light-ink layer, which
        # install.sh copies beside this theme.
        target.joinpath(SYMBOLIC_DIR).symlink_to(
            os.path.join("..", DARK_DIR, SYMBOLIC_DIR))
        symbolic = len(list(read_contract()))

    dirs = {str(Path(relative).parent) for relative, _d in links} | set(mirrored)
    dirs = sorted(dirs, key=order)
    scaled = [d for d in dirs if "@2x" in d]
    heavy = [d for d in dirs if "@2x" not in d]
    if dark:
        heavy = sorted(set(heavy) | set(symbolic_entries()), key=order)

    inherits = [BASE_DIR]
    if dark:
        inherits = [DARK_DIR, BASE_DIR]
    write_index(target, name, comment, ",".join(inherits + ["AdwaitaLegacy", "hicolor"]),
                heavy, scaled, base_sections()[2])
    return len(links), len(mirrored), symbolic


def build(quiet: bool = False) -> int:
    symbolic, dark_mirrored = build_dark()
    if not quiet:
        print(f"{DARK_DIR}: {symbolic} light-ink symbolic files, "
              f"{dark_mirrored} coloured trees mirrored from {BASE_DIR}")
    for directory, name, comment, accent, dark in variant_names():
        if accent is None:
            continue
        links, mirrored, symbolic_links = build_accent(directory, name, comment,
                                                       accent, dark)
        if not quiet:
            detail = (f"{links} accent symlinks, {mirrored} coloured trees "
                      f"mirrored from {BASE_DIR}")
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
        expected_links = {r for r, _d in variant_links(accent)} if accent else set()
        owned = {str(Path(relative).parent) for relative in expected_links}
        links: set[str] = set()
        mirrors: set[str] = set()
        holding: set[str] = set()
        for root, subdirs, files in os.walk(target, followlinks=False):
            base = Path(root)
            for child in list(subdirs):
                path = base / child
                if path.is_symlink():
                    subdirs.remove(child)  # a mirrored tree, not ours to walk
                    if child != SYMBOLIC_DIR:
                        mirrors.add(str(path.relative_to(target)))
            for name_ in files:
                if name_ == "index.theme":
                    continue
                holding.add(str(base.relative_to(target)))
                if (base / name_).is_symlink():
                    links.add(str((base / name_).relative_to(target)))
        for want in sorted(expected_links - links):
            problems.append(f"{directory}/{want}: accent symlink missing")
        for extra in sorted(links - expected_links):
            problems.append(f"{directory}/{extra}: symlink not in the accent map")
        expected_mirrors = (set(inherited_dirs()) - owned
                           - (ACCENT_SKIP if accent else set()))
        for want in sorted(expected_mirrors - mirrors):
            problems.append(f"{directory}/{want}: coloured context not mirrored")
        for extra in sorted(mirrors - set(inherited_dirs())):
            problems.append(f"{directory}/{extra}: mirrored directory is not one "
                            f"{BASE_DIR}/index.theme declares")
        for entry in sorted(expected_mirrors & mirrors):
            link = target / entry
            want = os.path.relpath(BASE / entry, link.parent)
            if os.readlink(link) != want:
                problems.append(f"{directory}/{entry}: points at "
                                f"{os.readlink(link)}, expected {want}")
        for link in target.rglob("*"):
            if link.is_symlink() and not link.exists():
                problems.append(f"{directory}/{link.relative_to(target)}: "
                                f"dangling -> {os.readlink(link)}")
        if dark:
            symbolic = target / SYMBOLIC_DIR
            if not symbolic.is_dir():
                problems.append(f"{directory}/symbolic: missing light-ink layer")
        declared = set()
        for line in text.splitlines():
            if line.startswith(("Directories=", "ScaledDirectories=")):
                declared |= {d for d in line.split("=", 1)[1].split(",") if d}
        for entry in sorted(declared):
            if not (target / entry).is_dir():
                problems.append(f"{directory}/{entry}: declared but missing")
        for entry in sorted(holding):
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
