#!/usr/bin/env python3
"""Draw a skeuomorphic icon for every GUI application installed here.

The app list is *discovered* from the freedesktop desktop entries
(``/usr/share/applications``, ``/usr/local/share/applications``, ``~/.local/share/applications``,
``~/.local/share/flatpak/exports/share/applications``), so the set stays in sync with what is
actually installed.  Each app becomes one **physical object** from
:mod:`skeu.apps` - a terminal, a steel desk globe, an envelope with a wax seal, a dark glass
key-cap, a film reel - lit and shadowed by the relief renderer in :mod:`skeu`.  There are no
monograms on coloured discs.

Apps that already have a hand-authored icon in ``svg/`` (Emacs, IntelliJ IDEA, Signal, 1Password)
reuse it instead of being re-invented.

    python3 tools/make_app_icons.py                # discover + build everything
    python3 tools/make_app_icons.py --list         # print the app table only
    python3 tools/make_app_icons.py --only Firefox GIMP
    python3 tools/make_app_icons.py --svg-only --jobs 8
"""

from __future__ import annotations

import argparse
import configparser
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from render_skeu import render, resize, seed_for, slugify  # noqa: E402
from skeu.apps import design  # noqa: E402

OUT = ROOT / "app-icons"
SVG_SRC = ROOT / "svg"

SIZES = (16, 32, 64, 128, 256, 512, 1024)

APP_DIRS = (
    "/usr/share/applications",
    "/usr/local/share/applications",
    str(Path.home() / ".local/share/applications"),
    str(Path.home() / ".local/share/flatpak/exports/share/applications"),
    "/var/lib/flatpak/exports/share/applications",
    "/var/lib/snapd/desktop/applications",
)

# ---------------------------------------------------------------- discovery

VERSION_RE = re.compile(r"\s+\d{4}\.\d+[\w.\- ]*(patch\s*\d+)?$", re.I)
GENERIC_VERSION_RE = re.compile(r"\s+v?\d+(\.\d+)+[\w.\- ]*$", re.I)


def normalise(name: str) -> str:
    """Strip trailing version junk so overrides and slugs stay stable."""
    out = VERSION_RE.sub("", name)
    out = GENERIC_VERSION_RE.sub("", out)
    return out.strip()


def discover() -> list[dict]:
    apps: dict[str, dict] = {}
    for directory in APP_DIRS:
        for path in sorted(glob.glob(directory + "/*.desktop")):
            cp = configparser.ConfigParser(interpolation=None, strict=False)
            try:
                cp.read(path, encoding="utf-8")
            except Exception:
                continue
            if not cp.has_section("Desktop Entry"):
                continue
            entry = cp["Desktop Entry"]
            if entry.get("NoDisplay", "").lower() == "true":
                continue
            if entry.get("Type", "Application") != "Application":
                continue
            display = entry.get("Name", Path(path).stem)
            name = normalise(display)
            if name in apps:                     # first hit wins (system before flatpak)
                continue
            exec_line = (entry.get("Exec", "") or "").strip()
            apps[name] = {
                "name": name,
                "display": display,
                "categories": entry.get("Categories", ""),
                "comment": (entry.get("Comment", "") or "").split("\u2014")[0][:70].strip(),
                "exec": exec_line.split()[0] if exec_line else "",
                "icon": entry.get("Icon", ""),
                "desktop": Path(path).name,
            }
    return [apps[k] for k in sorted(apps)]


# Apps with a hand-authored icon already in svg/ - reused verbatim.
REUSE = {
    "1Password": "1Password",
    "Emacs": "Emacs",
    "Emacs (Client)": "Emacs",
    "IntelliJ IDEA": "IntelliJ IDEA",
    "Signal": "Signal",
}

#: Historical artwork that beats anything drawn from scratch: the icon the app
#: actually shipped in its own era, recoloured into this pack's material palette.
HISTORY: dict[str, Path] = {}


def choose(app: dict) -> tuple[str, object, dict]:
    """Return ``(kind, builder-or-source, kwargs)`` for one application."""
    if app["name"] in REUSE:
        return "hand-authored", REUSE[app["name"]], {}
    if app["name"] in HISTORY:
        return "historical", HISTORY[app["name"]], {}
    builder, kwargs = design(app["name"], app["categories"], app["comment"])
    return "object", builder, kwargs


# ---------------------------------------------------------------- build

def render_svg(svg: Path, size: int, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["inkscape", "--export-type=png", f"--export-filename={out}",
         f"--export-width={size}", f"--export-height={size}", str(svg)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def build_one(item: tuple[str, str, object, dict, bool]) -> str:
    """Render one app: an object or a hand-drawn SVG."""
    name, slug, builder, kwargs, svg_only = item
    folder = OUT / slug
    folder.mkdir(parents=True, exist_ok=True)
    stale = folder / "icon.svg"
    if stale.is_file():
        stale.unlink()

    if isinstance(builder, Path):                      # hand-authored SVG
        target = folder / "icon.svg"
        shutil.copy2(builder, target)
        if not svg_only:
            for size in SIZES:
                render_svg(target, size, folder / f"icon-{size}.png")
        return slug

    image = render(builder, kwargs, seed=seed_for(slug))
    if not svg_only:
        for size in SIZES:
            resize(image, size).save(folder / f"icon-{size}.png")
    return slug


def contact_sheet(entries: list[dict], columns: int = 10) -> None:
    tiles = [OUT / e["slug"] / "icon-256.png" for e in entries
             if (OUT / e["slug"] / "icon-256.png").is_file()]
    if not tiles:
        return
    rows = math.ceil(len(tiles) / columns)
    sheet = Image.new("RGBA", (columns * 172 + 12, rows * 188 + 12), (58, 58, 60, 255))
    for i, png in enumerate(tiles):
        with Image.open(png) as im:
            rgba = im.convert("RGBA").resize((160, 160), Image.LANCZOS)
            sheet.paste(rgba, (12 + (i % columns) * 172, 12 + (i // columns) * 188), rgba)
    sheet.save(OUT / "contact-sheet.png")


def design_record(kind: str, builder, kwargs: dict) -> dict:
    if kind == "hand-authored":
        return {"kind": "hand-authored", "source": builder}
    if kind == "historical":
        return {"kind": "historical",
                "source": str(Path(builder).relative_to(LIBRARY))}
    return {
        "kind": "object",
        "object": getattr(builder, "__name__", "object"),
        "hue": kwargs.get("hue"),
        "archetype": "still-life object",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None, help="app names to build")
    parser.add_argument("--list", action="store_true", help="print the app table and exit")
    parser.add_argument("--svg-only", action="store_true", help="skip rasterising")
    parser.add_argument("--jobs", type=int, default=min(10, os.cpu_count() or 1))
    args = parser.parse_args(argv)

    apps = discover()
    plan: list[tuple[dict, str, str, object, dict]] = []
    for app in apps:
        kind, builder, kwargs = choose(app)
        plan.append((app, slugify(app["name"]), kind, builder, kwargs))

    if args.list:
        print(f"{len(apps)} installed applications\n")
        for app, slug, kind, builder, kwargs in plan:
            if kind == "hand-authored":
                how = f"hand-authored ({builder})"
            elif kind == "historical":
                how = f"historical ({Path(builder).name})"
            else:
                how = f"{getattr(builder, '__name__', 'object'):18s} hue {int(kwargs.get('hue') or 0):3d}"
            print(f'  {app["name"]:34s} {how}')
        return 0

    if not args.only:
        # wipe the per-app folders but keep README.md and the contact sheet name
        for child in OUT.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
    wanted = {w.lower() for w in (args.only or [])}
    selected = [(app, slug, kind, builder, kwargs) for app, slug, kind, builder, kwargs in plan
                if not wanted or app["name"].lower() in wanted or slug in wanted]

    items = []
    for app, slug, kind, builder, kwargs in selected:
        if kind == "hand-authored":
            items.append((app["name"], slug, SVG_SRC / f"{builder}.svg", {}, args.svg_only))
        elif kind == "historical":
            items.append((app["name"], slug, Path(builder), {}, args.svg_only))
        else:
            items.append((app["name"], slug, builder, kwargs, args.svg_only))

    with Pool(min(args.jobs, max(1, len(items)))) as pool:
        for slug in pool.imap_unordered(build_one, items):
            print(f"  {slug}")

    entries = []
    for app, slug, kind, builder, kwargs in selected:
        entries.append({
            "name": app["name"],
            "display": app["display"],
            "slug": slug,
            "categories": app["categories"],
            "comment": app["comment"],
            "exec": app["exec"],
            "desktop": app["desktop"],
            "design": design_record(kind, builder, kwargs),
            "files": {"png": f"{slug}/icon-1024.png"},
        })

    index_path = OUT / "index.json"
    previous = {}
    if index_path.is_file():
        previous = {e["slug"]: e for e in json.loads(index_path.read_text()).get("apps", [])}
    merged = dict(previous)
    for entry in entries:
        merged[entry["slug"]] = entry

    index_path.write_text(json.dumps({
        "generator": "tools/make_app_icons.py",
        "renderer": "tools/skeu (relief renderer, no icon mask)",
        "discovered_from": [d for d in APP_DIRS if Path(d).is_dir()],
        "count": len(merged),
        "objects": sorted({e["design"].get("object", e["design"].get("source"))
                           for e in merged.values()}),
        "apps": [merged[k] for k in sorted(merged)],
    }, indent=2, ensure_ascii=False) + "\n")

    if not args.svg_only:
        contact_sheet([merged[k] for k in sorted(merged)])
    print(f"done: {len(entries)} icon(s) built, {len(merged)} indexed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
