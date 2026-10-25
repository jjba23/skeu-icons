#!/usr/bin/env python3
"""Render the generated artwork with the relief renderer.

    python3 tools/render_skeu.py                     # categories + devices + projects
    python3 tools/render_skeu.py --only categories   # one group
    python3 tools/render_skeu.py --only maak skeu-icons
    python3 tools/render_skeu.py --sheet              # contact sheets in /tmp/skeu

Categories and devices land in ``generated/<slug>.png`` (1024 px).  Projects become
a full set in ``project-icons/<slug>/`` (16-1024 px) plus ``index.json``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from skeu.catalog import CATEGORIES, DEVICES, PROJECTS  # noqa: E402
from skeu.paint import Canvas  # noqa: E402

SIZES = (16, 32, 64, 128, 256, 512, 1024)


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def render(builder, kwargs: dict, seed: int) -> Image.Image:
    canvas = Canvas(seed=seed)
    builder(canvas, **kwargs)
    return normalise(canvas.finish())


def normalise(image: Image.Image, fill: float = 0.80, centre=(512, 474)) -> Image.Image:
    """Give every icon the same optical size: the object fills ~80 % of the canvas.

    The builders draw at their natural size, which leaves some devices looking
    lost in the corner. Rather than hand-tuning eighty numbers, find the solid
    silhouette, scale it, and re-centre it slightly above the middle so the cast
    shadow still fits.
    """
    alpha = image.getchannel("A")
    solid = alpha.point(lambda v: 255 if v >= 140 else 0)
    box = solid.getbbox()
    if box is None:
        return image
    bx0, by0, bx1, by1 = box
    pad = 150
    x0, y0 = max(0, bx0 - pad), max(0, by0 - pad)
    x1, y1 = min(image.width, bx1 + pad), min(image.height, by1 + pad)
    crop = image.crop((x0, y0, x1, y1))
    scale = (fill * image.width) / max(bx1 - bx0, by1 - by0)
    size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
    crop = crop.resize(size, Image.LANCZOS)
    # where the object centre lands inside the scaled crop, then move it to `centre`
    left = round(centre[0] - ((bx0 + bx1) / 2 - x0) * scale)
    top = round(centre[1] - ((by0 + by1) / 2 - y0) * scale)
    out = Image.new("RGBA", image.size, (0, 0, 0, 0))
    out.alpha_composite(crop, (left, top))
    return out


def seed_for(slug: str) -> int:
    return zlib.crc32(slug.encode()) % 997 + 1


def resize(image: Image.Image, size: int) -> Image.Image:
    """Downsample, then put back the crispness Lanczos takes out.

    The small sizes are not blurred versions of the big one: they get a two-stage
    resample, a stronger unsharp mask and a touch more chroma, so the silhouette
    and the one internal shape still separate at 16 px.
    """
    if size <= 32:
        stage = image.resize((size * 4, size * 4), Image.LANCZOS)
        small = stage.resize((size, size), Image.LANCZOS)
        small = small.filter(ImageFilter.UnsharpMask(radius=0.6, percent=110, threshold=0))
        small = ImageEnhance.Color(small).enhance(1.08)
        small = ImageEnhance.Contrast(small).enhance(1.05)
        return small
    if size <= 64:
        small = image.resize((size, size), Image.LANCZOS)
        return small.filter(ImageFilter.UnsharpMask(radius=0.7, percent=70, threshold=0))
    return image.resize((size, size), Image.LANCZOS)


def build_generated(item: tuple[str, object, dict]) -> str:
    slug, builder, kwargs = item
    out = ROOT / "generated" / f"{slug}.png"
    render(builder, kwargs, seed_for(slug)).save(out)
    return slug


def build_project(item: tuple[str, str, object, dict]) -> str:
    name, purpose, builder, kwargs = item
    slug = slugify(name)
    folder = ROOT / "project-icons" / slug
    folder.mkdir(parents=True, exist_ok=True)
    stale = folder / "icon.svg"
    if stale.is_file():
        stale.unlink()
    image = render(builder, kwargs, seed_for(slug))
    for size in SIZES:
        resize(image, size).save(folder / f"icon-{size}.png")
    return slug


def project_entries() -> list[dict]:
    """The index records for every project, in catalogue order."""
    entries = []
    for name, purpose, builder, kwargs in PROJECTS:
        slug = slugify(name)
        entries.append({
            "name": name,
            "slug": slug,
            "purpose": purpose,
            "object": getattr(builder, "__name__", "object"),
            "files": {
                "png": f"{slug}/icon-1024.png",
            },
        })
    return entries


def write_project_index(entries: list[dict]) -> None:
    (ROOT / "project-icons" / "index.json").write_text(json.dumps({
        "generator": "tools/render_skeu.py",
        "style": "skeuomorphic, no icon mask",
        "count": len(entries),
        "objects": len({e["object"] for e in entries}),
        "icons": entries,
    }, indent=2, ensure_ascii=False) + "\n")


def contact_sheet(paths: list[Path], target: Path, columns: int = 8,
                  tile: int = 200) -> None:
    if not paths:
        return
    rows = math.ceil(len(paths) / columns)
    sheet = Image.new("RGBA", (columns * (tile + 8) + 8, rows * (tile + 8) + 8),
                      (58, 58, 61, 255))
    for i, path in enumerate(paths):
        with Image.open(path) as image:
            thumb = image.convert("RGBA").resize((tile, tile), Image.LANCZOS)
        sheet.alpha_composite(thumb, (8 + (i % columns) * (tile + 8),
                                      8 + (i // columns) * (tile + 8)))
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None,
                        help="group names (categories/devices/projects) or slugs")
    parser.add_argument("--sheet", action="store_true", help="write contact sheets")
    parser.add_argument("--jobs", type=int, default=min(10, os.cpu_count() or 1))
    parser.add_argument("--sheet-dir", type=Path, default=Path("/tmp/skeu"))
    args = parser.parse_args(argv)

    wanted = set(args.only or [])
    started = time.time()

    generated = [(slug, builder, kwargs) for slug, (builder, kwargs) in CATEGORIES.items()]
    generated += [(slug, builder, kwargs) for slug, (builder, kwargs) in DEVICES.items()]
    projects = [(name, purpose, builder, kwargs) for name, purpose, builder, kwargs in PROJECTS]

    group_of = {slug: "categories" for slug in CATEGORIES}
    group_of.update({slug: "devices" for slug in DEVICES})
    chosen_generated = [item for item in generated
                        if not wanted or group_of[item[0]] in wanted or item[0] in wanted]
    chosen_projects = [item for item in projects
                       if not wanted or "projects" in wanted or slugify(item[0]) in wanted]
    do_generated = bool(chosen_generated)

    if do_generated:
        with Pool(args.jobs) as pool:
            done = pool.map(build_generated, chosen_generated)
        print(f"generated: {len(done)} icon(s)")

    if chosen_projects:
        with Pool(args.jobs) as pool:
            done = pool.map(build_project, chosen_projects)
        write_project_index(project_entries())
        print(f"projects: {len(done)} icon(s)")

    if args.sheet:
        for group, pattern, target in (
                ("categories", [ROOT / "generated" / f"{s}.png" for s in CATEGORIES],
                 args.sheet_dir / "categories.png"),
                ("devices", [ROOT / "generated" / f"{s}.png" for s in DEVICES],
                 args.sheet_dir / "devices.png"),
                ("projects", [ROOT / "project-icons" / slugify(n) / "icon-256.png"
                              for n, *_ in projects], args.sheet_dir / "projects.png")):
            contact_sheet([p for p in pattern if p.is_file()], target)
            print(f"sheet: {target}")

    print(f"done in {time.time() - started:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
