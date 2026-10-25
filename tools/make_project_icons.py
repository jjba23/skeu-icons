#!/usr/bin/env python3
"""Render the project icons with the relief renderer.

Each project has one *physical object* chosen from what the project does - a
stopwatch for the CI orchestrator, a keyring for the secrets tool, a balance for
the test framework - and the object is lit, shaded and shadowed by
:mod:`skeu.paint`.  Nothing is a monogram on a coloured plate.

    python3 tools/make_project_icons.py                 # every project
    python3 tools/make_project_icons.py --only maak veritas
    python3 tools/make_project_icons.py --install       # + .directory in each project

Output: project-icons/<slug>/icon-{16..1024}.png, index.json,
contact-sheet.png.
"""

from __future__ import annotations

import argparse
import sys
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_skeu import (build_project, contact_sheet, project_entries,  # noqa: E402
                         slugify, write_project_index)
from skeu.catalog import PROJECTS  # noqa: E402


def install(entries) -> None:
    for entry in entries:
        target = Path.home() / "Hacking" / entry["name"]
        if not target.is_dir():
            print(f"  skip (not a directory): {target}")
            continue
        icon = (ROOT / "project-icons" / entry["slug"] / "icon-256.png").resolve()
        (target / ".directory").write_text(
            "[Desktop Entry]\n"
            "Type=Directory\n"
            f'Name={entry["name"]}\n'
            f"Icon={icon}\n"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None, help="project names or slugs")
    parser.add_argument("--install", action="store_true",
                        help="also write a .directory into each ~/Hacking/<project>")
    parser.add_argument("--jobs", type=int, default=10)
    args = parser.parse_args(argv)

    wanted = set(args.only or [])
    items = [item for item in PROJECTS
             if not wanted or item[0] in wanted or slugify(item[0]) in wanted]
    if not items:
        parser.error(f"no project matched {sorted(wanted)}")

    with Pool(min(args.jobs, len(items))) as pool:
        pool.map(build_project, items)
    entries = project_entries()
    write_project_index(entries)
    contact_sheet([ROOT / "project-icons" / e["slug"] / "icon-256.png" for e in entries],
                  ROOT / "project-icons" / "contact-sheet.png")

    if args.install:
        install(entries)
        print(f"installed .directory files into {len(entries)} project folders")
    print(f"done: {len(items)} built, {len(entries)} indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
