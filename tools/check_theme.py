#!/usr/bin/env python3
"""Verify what is on disk: index.theme, every directory, counts and the gallery.

Run it after redrawing anything; it is the same checks ``maak check`` runs.

    python3 tools/check_theme.py            # human summary, exit 1 on problems
    python3 tools/check_theme.py --quiet    # only problems

Checks, in order:

* the theme directory and ``index.theme`` exist, and the header keys are sane;
* ``Directories=``/``ScaledDirectories=`` are unique, exist on disk, are not
  empty, and have a matching section carrying ``Size``, ``Context`` and ``Type``
  (plus ``Scale=2`` for scaled dirs, ``MinSize``/``MaxSize`` for scalable ones);
* every section belongs to a declared directory, and every ``Context=`` value is
  one the freedesktop spec defines;
* the six contexts carry the same icon names at every fixed size;
* the symbolic layer matches ``tools/symbolic-names.txt`` exactly, name for name
  and byte for byte (see ``tools/make_symbolic.py``), and carries no extras;
* the accent/lightness variants in ``skeu-icons-green`` and
  ``skeu-icons-green-dark`` are intact: index.theme, accent symlinks, no
  dangling links, and the full light-ink symbolic set;
* a table of real file names (``.zip``, ``.tar.gz``, ``.tar.xz``, ``.flac``,
  ``.docx`` …) resolves to the artwork it should: each one is run through GIO,
  the way a file manager does it, and the whole icon chain is checked against
  the theme (see ``tools/check_mapping.py``);
* ``app-icons/`` and ``project-icons/`` match their ``index.json`` (count and
  every ``icon-<size>.png``), and ``theme-manifest.json`` matches the disk;
* no ``.icns`` file has crept back in;
* ``gallery.html`` is up to date with the icons on disk;
* the counts ``README.org`` quotes still match the theme (see
  ``tools/make_readme_counts.py``).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = "skeu-icons"
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
SET_SIZES = (16, 32, 64, 128, 256, 512)
CONTEXTS = ("apps", "places", "mimetypes", "emblems", "categories", "devices")
SYMBOLIC_CONTEXTS = ("actions", "categories", "devices", "emotes", "legacy",
                     "mimetypes", "places", "status", "ui")
#: Contexts whose un-suffixed icons are drawn as scalable SVG (the rest ship
#: relief bitmaps); kept in step with tools/make_plain.py by its own check.
PLAIN_CONTEXTS = ("actions", "emotes", "legacy", "status", "ui")
FREEDESKTOP_CONTEXTS = {
    "Actions", "Animations", "Applications", "Categories", "Devices", "Emblems",
    "Emotes", "Filesystems", "International", "Legacy", "MimeTypes", "Places",
    "Status", "Stock", "UI",
}

sys.path.insert(0, str(Path(__file__).resolve().parent))


def parse_index(path: Path) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """``(header, sections)`` for an ``index.theme`` file."""
    header: dict[str, str] = {}
    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            if current != "Icon Theme":
                sections[current] = {}
            else:
                current = None
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        if current is None:
            header[key] = value
        else:
            sections[current][key] = value
    return header, sections


def check() -> list[str]:
    problems: list[str] = []
    theme = ROOT / THEME
    index = theme / "index.theme"

    if not theme.is_dir():
        return [f"missing theme directory: {THEME}/"]
    if not index.is_file():
        return [f"missing {THEME}/index.theme"]

    header, sections = parse_index(index)
    for key in ("Name", "Comment", "Inherits", "Example"):
        if key not in header:
            problems.append(f"index.theme: missing {key}=")
    if "hicolor" not in header.get("Inherits", ""):
        problems.append("index.theme: Inherits= should end with hicolor")

    declared: list[str] = []
    for key in ("Directories", "ScaledDirectories"):
        declared += [d for d in header.get(key, "").split(",") if d]
    if not declared:
        problems.append("index.theme: no Directories= entries")
    if len(declared) != len(set(declared)):
        problems.append("index.theme: duplicate directory entries")

    for directory in declared:
        path = theme / directory
        section = sections.get(directory)
        if not path.is_dir():
            problems.append(f"{directory}: declared but missing on disk")
            continue
        if not any(path.iterdir()):
            problems.append(f"{directory}: empty")
        if section is None:
            problems.append(f"{directory}: declared but has no [{directory}] section")
            continue
        for key in ("Size", "Context", "Type"):
            if key not in section:
                problems.append(f"[{directory}]: missing {key}=")
        if section.get("Context", "") not in FREEDESKTOP_CONTEXTS:
            problems.append(f"[{directory}]: unknown Context={section.get('Context')}")
        if "@2x" in directory and section.get("Scale") != "2":
            problems.append(f"[{directory}]: scaled directory without Scale=2")
        if section.get("Type") == "Scalable":
            for key in ("MinSize", "MaxSize"):
                if key not in section:
                    problems.append(f"[{directory}]: Type=Scalable without {key}=")

    for directory in sections:
        if directory not in declared:
            problems.append(f"[{directory}]: section for an undeclared directory")

    # every context should carry the same names at every fixed size
    for context in CONTEXTS:
        per_size = {}
        for size in SIZES:
            folder = theme / f"{size}x{size}" / context
            per_size[size] = {p.stem for p in folder.glob("*.png")} if folder.is_dir() else set()
        if not per_size[SIZES[0]]:
            problems.append(f"{context}: no icons at {SIZES[0]}px")
            continue
        reference = per_size[SIZES[0]]
        for size in SIZES[1:]:
            missing = reference - per_size[size]
            if missing:
                problems.append(f"{context}: {len(missing)} name(s) missing at {size}px "
                                f"(e.g. {sorted(missing)[0]})")

    # the example icon must actually exist
    example = header.get("Example")
    if example and not any((theme / f"{s}x{s}").rglob(f"{example}.png") for s in (SIZES[0],)):
        problems.append(f"index.theme: Example={example} does not resolve")

    # the two extra sets
    for path, key in (("app-icons/index.json", "apps"), ("project-icons/index.json", "icons")):
        data_path = ROOT / path
        if not data_path.is_file():
            problems.append(f"missing {path}")
            continue
        data = json.loads(data_path.read_text())
        records = data[key]
        if data.get("count") != len(records):
            problems.append(f"{path}: count={data.get('count')} but {len(records)} records")
        for record in records:
            folder = data_path.parent / record["slug"]
            if not folder.is_dir():
                problems.append(f"{path}: {record['slug']}/ missing")
                continue
            for size in SET_SIZES:
                if not (folder / f"icon-{size}.png").is_file():
                    problems.append(f"{record['slug']}/icon-{size}.png missing")
                    break

    # the manifest audit trail
    manifest_path = ROOT / "theme-manifest.json"
    if not manifest_path.is_file():
        problems.append("missing theme-manifest.json")
    else:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("theme_name") != header.get("Name"):
            problems.append("theme-manifest.json: theme_name does not match index.theme")
        counts = {c: len({p.stem for p in (theme / f"{SIZES[-1]}x{SIZES[-1]}" / c).glob("*.png")})
                  for c in CONTEXTS}
        if manifest.get("contexts") != counts:
            problems.append(f"theme-manifest.json: contexts {manifest.get('contexts')} "
                            f"but disk has {counts}")
        if manifest.get("icons") != sum(counts.values()):
            problems.append("theme-manifest.json: icons total does not match the disk")
        symbolic_counts = {c: len(list((theme / "symbolic" / c).glob("*.svg")))
                           for c in SYMBOLIC_CONTEXTS if (theme / "symbolic" / c).is_dir()}
        symbolic_manifest = manifest.get("symbolic") or {}
        if symbolic_manifest.get("contexts") != dict(sorted(symbolic_counts.items())):
            problems.append("theme-manifest.json: symbolic contexts do not match the disk")
        if symbolic_manifest.get("icons") != sum(symbolic_counts.values()):
            problems.append("theme-manifest.json: symbolic total does not match the disk")
        if not (manifest.get("variants") or {}).get("themes"):
            problems.append("theme-manifest.json: variants are not listed")

    # nothing .icns may come back
    stray = sorted(p for p in ROOT.rglob("*.icns") if ".git" not in p.parts)
    if stray:
        problems.append(f"{len(stray)} .icns file(s) present (e.g. {stray[0].relative_to(ROOT)})")

    # the symbolic layer and the variants are generated; verify them here so
    # one `maak check` covers everything that ships.
    try:
        from make_plain import check as check_plain
        from make_symbolic import check as check_symbolic
        from make_variants import check as check_variants
    except Exception as error:  # noqa: BLE001
        problems.append(f"cannot import the generators: {error}")
    else:
        problems += check_symbolic()
        problems += check_plain()
        problems += check_variants()

    # what a file manager actually asks for, walked through GIO
    try:
        from check_mapping import check as check_mapping
    except Exception as error:  # noqa: BLE001
        problems.append(f"cannot import tools/check_mapping.py: {error}")
    else:
        problems += check_mapping(quiet=True)

    # the gallery must match what the generator produces
    try:
        from make_gallery import OUT, build
    except Exception as error:  # noqa: BLE001
        problems.append(f"cannot import tools/make_gallery.py: {error}")
    else:
        if not OUT.is_file():
            problems.append("gallery.html missing - run: python3 tools/make_gallery.py")
        elif OUT.read_text() != build():
            problems.append("gallery.html is stale - run: python3 tools/make_gallery.py")

    # the counts README.org quotes are derived from the theme, not typed
    try:
        from make_readme_counts import drift
    except Exception as error:  # noqa: BLE001
        problems.append(f"cannot import tools/make_readme_counts.py: {error}")
    else:
        problems += drift()

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="print only problems")
    args = parser.parse_args(argv)

    problems = check()
    if problems:
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(f"\n{len(problems)} problem(s) found", file=sys.stderr)
        return 1
    if not args.quiet:
        header, sections = parse_index(ROOT / THEME / "index.theme")
        symbolic = sum(len(list((ROOT / THEME / "symbolic" / c).glob("*.svg")))
                       for c in SYMBOLIC_CONTEXTS
                       if (ROOT / THEME / "symbolic" / c).is_dir())
        plain = sum(len(list((ROOT / THEME / "scalable" / c).glob("*.svg")))
                    for c in PLAIN_CONTEXTS
                    if (ROOT / THEME / "scalable" / c).is_dir())
        variants = len(list(ROOT.glob("skeu-icons-*/index.theme")))
        print(f"ok: {header.get('Name')} - {len(sections)} directories, "
              f"{len(SIZES)} sizes x {len(CONTEXTS)} contexts, {symbolic} symbolic "
              f"icons, {plain} plain scalable icons, {variants} variant themes, "
              f"gallery current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
