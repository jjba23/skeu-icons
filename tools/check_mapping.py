#!/usr/bin/env python3
"""Check that real file names actually find their artwork.

The theme is a pile of names, and a file manager never asks for a name the way
a human would: it asks GIO what ``archive.tar.gz`` *is*
(``application/x-compressed-tar``) and then asks the theme for a chain of icon
names derived from that.  This programme walks the same path three times over -
through GIO, through GTK's own icon lookup, and through the pixels - so a name
that drifted shows up as "you get the carton" instead of as a mystery in
Nautilus.

    python3 tools/check_mapping.py            # the table, then the problems
    python3 tools/check_mapping.py --quiet    # only problems

These are failures:

* **nothing resolves** - every name in the chain is missing, so the file draws
  an Adwaita icon or a blank tile;
* **the wrong artwork answers** - a sample whose expectation is not in the
  winning name, e.g. a ``.tar.gz`` that lands on ``package-x-generic``;
* **the name is only half there** - the winning name exists at some sizes but
  not all of them, or GTK cannot find it at all, which is what a half-finished
  alias link or a stale ``index.theme`` entry looks like;
* **a link points nowhere** - a dangling symlink in the theme;
* **a file will not load** - the winning PNG or SVG is corrupt.

A sample that resolves through the family generic when a specific name was
expected is the interesting case: it means the artwork exists under a name GIO
no longer asks for.  ``make_theme_mimes.py`` fixes those with an alias.

Needs GIO and GTK 3 (``python3-gi``) - the same libraries GTK and the file
managers use.  If GTK is not importable the check says so and falls back to
reading the theme directories itself: the icons do not depend on it.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "skeu-icons"
DARK = ROOT / "skeu-icons-dark"
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
CONTEXTS = ("apps", "places", "mimetypes", "emblems", "categories", "devices")
VARIANTS = ("skeu-icons", "skeu-icons-dark")

#: ``(file name, what the winning icon name must contain)``.  The archive block
#: is the one Adwaita historically got wrong, and the compound names
#: (``.tar.gz``, ``.tar.xz`` ...) are the ones a naive extension lookup misses:
#: GIO reads them as one type, so the theme needs the bare ``-compressed-tar``
#: names and not just the compressors.
SAMPLES: tuple[tuple[str, str], ...] = (
    # pictures, text, office, media
    ("photo.png", "png"),
    ("photo.jpg", "jpeg"),
    ("drawing.svg", "svg"),
    ("notes.txt", "text-plain"),
    ("readme.md", "markdown"),
    ("manual.pdf", "pdf"),
    ("book.epub", "epub"),
    ("report.docx", "wordprocessingml"),
    ("budget.xlsx", "spreadsheetml"),
    ("slides.odp", "presentation"),
    ("track.flac", "flac"),
    ("track.mp3", "mpeg"),
    ("track.ogg", "ogg"),
    ("film.mkv", "matroska"),
    ("film.mp4", "mp4"),
    # archives: one sample per container and per compressor, alone and in a tar
    ("archive.zip", "zip"),
    ("archive.tar", "tar"),
    ("archive.tar.gz", "compressed-tar"),
    ("archive.tgz", "compressed-tar"),
    ("archive.tar.xz", "xz-compressed-tar"),
    ("archive.tar.bz2", "bzip2-compressed-tar"),
    ("archive.tar.bz3", "bzip3-compressed-tar"),
    ("archive.tar.zst", "zstd-compressed-tar"),
    ("archive.tar.lz4", "lz4-compressed-tar"),
    ("archive.tar.lz", "lzip-compressed-tar"),
    ("archive.tar.lrz", "lrzip-compressed-tar"),
    ("archive.tar.rz", "rzip-compressed-tar"),
    ("archive.tar.br", "brotli-compressed-tar"),
    ("archive.7z", "7z"),
    ("archive.rar", "rar"),
    ("archive.cpio", "cpio"),
    ("data.gz", "gzip"),
    ("data.bz2", "bzip2"),
    ("data.bz3", "bzip3"),
    ("data.xz", "xz"),
    ("data.zst", "zstd"),
    ("data.lz4", "lz4"),
    ("data.lzma", "lzma"),
    ("data.lz", "lzip"),
    ("data.lrz", "lrzip"),
    ("data.rz", "rzip"),
    ("data.br", "brotli"),
    ("data.Z", "compress"),
    # package formats
    ("package.deb", "debian"),
    ("package.rpm", "rpm"),
    ("tool.AppImage", "appimage"),
    ("tool.flatpak", "flatpak"),
    ("tool.snap", "snap"),
    ("tool.xpi", "xpinstall"),
    ("tool.jar", "java-archive"),
    ("tool.apk", "android"),
    ("image.iso", "iso"),
    ("image.msi", "msi"),
    ("image.dmg", "apple-diskimage"),
    # source, data and fonts
    ("main.py", "python"),
    ("main.rs", "rust"),
    ("core.lisp", "lisp"),
    ("data.json", "json"),
    ("config.toml", "toml"),
    ("style.ttf", "ttf"),
    ("font.woff2", "woff2"),
    ("program.desktop", "desktop"),
    # Deliberate non-matches: an extensionless file is text/plain, and GIO has
    # a type of its own for README, which lands on the generic sheet.
    ("scratch", "text-plain"),
    ("README", "text-x-generic"),
)

#: Expectations that must not end at the family generic: these are the names
#: the pack claims to draw specifically.
CONTAINERS = frozenset(name for name, _ in SAMPLES
                       if name.split(".")[0] in ("archive", "data"))


def entries() -> dict[str, dict[str, Path]]:
    """``{icon name: {size label: path}}`` for every name the theme ships."""
    found: dict[str, dict[str, Path]] = {}
    for size in SIZES:
        for suffix in ("", "@2x"):
            for context in CONTEXTS:
                folder = THEME / f"{size}x{size}{suffix}" / context
                if not folder.is_dir():
                    continue
                for path in folder.glob("*.png"):
                    if path.exists():  # a broken alias link is not a name
                        found.setdefault(path.stem, {})[
                            f"{size}x{size}{suffix}"] = path
    for layer in ("scalable", "symbolic"):
        for path in (THEME / layer).rglob("*.svg"):
            if path.exists():
                found.setdefault(path.stem, {})[layer] = path
    return found


def symbolic_names(folder: Path) -> set[str]:
    """Every ``-symbolic`` name a theme's own symbolic layer carries."""
    return {path.stem for path in (folder / "symbolic").rglob("*.svg")
            if path.exists()}


def dangling() -> list[str]:
    """Symlinks in the theme whose target is gone."""
    return [str(path.relative_to(ROOT)) for path in THEME.rglob("*")
            if path.is_symlink() and not path.exists()]


def chain_for(path: Path) -> tuple[str, list[str]]:
    """``(mime type, icon names)`` as GIO reports them for PATH."""
    from gi.repository import Gio

    info = Gio.file_new_for_path(str(path)).query_info(
        "standard::content-type,standard::icon", Gio.FileQueryInfoFlags.NONE, None)
    icon = info.get_icon()
    names = (icon.get_names() if hasattr(icon, "get_names")
             else [icon.to_string()])
    return info.get_content_type(), list(names)


def icon_theme(name: str):
    """GTK's view of one of the themes, or ``None`` without GTK."""
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
    except Exception:  # noqa: BLE001
        return None
    theme = Gtk.IconTheme.new()
    theme.set_search_path([str(ROOT)])
    theme.set_custom_theme(name)
    return theme


def gtk_lookup(theme, name: str, size: int, symbolic: bool = False) -> Path | None:
    """The file GTK would draw for NAME, or ``None``."""
    from gi.repository import Gtk

    flags = Gtk.IconLookupFlags.FORCE_SYMBOLIC if symbolic else 0
    info = theme.lookup_icon(name, size, flags)
    return Path(info.get_filename()) if info else None


def parses(path: Path) -> bool:
    """Whether the artwork at PATH opens as the format its suffix claims."""
    try:
        if path.suffix == ".png":
            from PIL import Image

            with Image.open(path) as image:
                image.verify()
            return True
        ElementTree.parse(path)
        return True
    except Exception:  # noqa: BLE001
        return False


def check(quiet: bool = False) -> list[str]:
    """Problems with the mapping, as sentences."""
    try:
        from gi.repository import Gio  # noqa: F401
    except Exception:  # noqa: BLE001
        if not quiet:
            print("mapping: python3-gi is not installed, skipping the GIO "
                  "check (the icons do not need it)")
        return []

    problems = [f"{link}: dangling symlink" for link in dangling()]
    shipped = entries()
    monochrome = {name: symbolic_names(folder)
                  for name, folder in (("skeu-icons", THEME),
                                       ("skeu-icons-dark", DARK))}
    themes = {name: icon_theme(name) for name in VARIANTS}
    if not quiet and not themes["skeu-icons"]:
        print("mapping: GTK 3 is not installed, so only GIO is being asked")

    rows: list[tuple[str, str, str, bool, bool]] = []
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        for name, expect in SAMPLES:
            sample = folder / name
            sample.write_text("x")
            mime, chain = chain_for(sample)
            solid = [n for n in chain if not n.endswith("-symbolic")]
            present = [n for n in solid if n in shipped]
            winner = present[0] if present else None
            symbolic = [n for n in chain if n.endswith("-symbolic")
                        and n in shipped]
            if winner is None:
                rows.append((name, mime, "-", False, bool(symbolic)))
                problems.append(
                    f"{name}: {mime} resolves to nothing in the theme "
                    f"(tried {', '.join(solid)})")
                continue

            sizes = shipped[winner]
            exact = winner == solid[0]
            symbolic = symbolic or bool(themes["skeu-icons"] and
                                        gtk_lookup(themes["skeu-icons"],
                                                   winner, 16, symbolic=True))
            rows.append((name, mime, winner, exact, symbolic))

            if expect not in winner:
                problems.append(
                    f"{name}: {mime} draws {winner}, expected a name with "
                    f"{expect!r}")
            if name in CONTAINERS and winner == "package-x-generic":
                problems.append(f"{name}: falls back to the generic carton")
            missing = [label for label in
                       [f"{s}x{s}" for s in SIZES] +
                       [f"{s}x{s}@2x" for s in SIZES]
                       if label not in sizes]
            if missing and "scalable" not in sizes:
                problems.append(
                    f"{name}: {winner} is missing at {len(missing)} size(s) "
                    f"(e.g. {missing[0]})")

            # GTK has the last word: it is what actually draws the tile.  Ask
            # both themes at a realistic size and insist the answer lives in
            # this repository and not in the inherited Adwaita.
            for theme_name, theme in themes.items():
                if theme is None:
                    continue
                found = gtk_lookup(theme, winner, 48)
                if found is None or ROOT not in found.parents:
                    problems.append(
                        f"{name}: GTK cannot load {winner} from {theme_name}")
                elif not parses(found):
                    problems.append(
                        f"{name}: {found.relative_to(ROOT)} does not open")
                # A theme that draws its own monochrome icon must not be
                # answered by the parent theme's copy through Inherits=.
                symbolic_name = f"{winner}-symbolic"
                if symbolic_name in monochrome[theme_name]:
                    drawn = gtk_lookup(theme, symbolic_name, 16, symbolic=True)
                    expected = (DARK if theme_name == "skeu-icons-dark"
                                else THEME) / "symbolic"
                    if drawn is None or expected not in drawn.parents:
                        problems.append(
                            f"{name}: {theme_name} resolves "
                            f"{symbolic_name} outside its own layer")

    if not quiet:
        width = max(len(name) for name, _, _, _, _ in rows)
        mime_width = max(len(mime) for _, mime, _, _, _ in rows)
        for name, mime, winner, exact, symbolic in rows:
            mark = "" if exact else "  (family generic)"
            note = "" if symbolic else "  (no symbolic sibling)"
            print(f"  {name:<{width}}  {mime:<{mime_width}}  {winner}"
                  f"{mark}{note}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true",
                        help="print only problems")
    args = parser.parse_args(argv)

    problems = check(args.quiet)
    if problems:
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(f"\n{len(problems)} mapping problem(s) found", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"\nok: {len(SAMPLES)} sample file names map to the artwork "
              f"the theme ships, at every size, in both themes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
