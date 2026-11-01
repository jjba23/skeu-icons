#!/usr/bin/env python3
"""Compose the images the README shows.

The pack ships thousands of icons; the README needs six contact sheets that
load quickly on Codeberg, so this script renders them from the *built* artwork
rather than from a design tool:

    python3 tools/make_doc_images.py          # -> docs/*.png

Sheets are drawn on the same warm paper gradient so the icons read like objects
standing on a surface instead of stickers on white.  Everything here is
read-only: it never redraws an icon, it only arranges the PNGs the generators
already produced.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"

FONT = "/usr/share/fonts/truetype/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/DejaVuSans-Bold.ttf"

INK = (74, 79, 86, 255)
DIM = (120, 126, 134, 255)


# --------------------------------------------------------------------------- #
# canvas
# --------------------------------------------------------------------------- #

def background(width: int, height: int) -> Image.Image:
    """A warm paper gradient with a soft key light from the upper left."""
    y = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    x = np.linspace(0.0, 1.0, width, dtype=np.float32)[None, :]
    top = np.array([248, 246, 242], dtype=np.float32)
    bottom = np.array([228, 225, 219], dtype=np.float32)
    rgb = top * (1.0 - y[..., None]) + bottom * y[..., None]
    glow = np.clip(1.0 - np.hypot((x - 0.30) * 1.1, (y - 0.18) * 0.9), 0.0, 1.0)
    rgb = rgb + glow[..., None] * 12.0
    rgb = np.clip(rgb, 0, 255).astype(np.uint8)
    sheet = Image.fromarray(np.dstack([rgb, np.full((height, width), 255, np.uint8)]),
                            "RGBA")
    return sheet


def load(path: Path, size: int) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.width != size:
        image = image.resize((size, size), Image.LANCZOS)
    return image


def place(sheet: Image.Image, icon: Image.Image, x: int, y: int) -> None:
    """Composite an icon with a tight contact shadow, at integer pixels."""
    size = icon.width
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow.paste((22, 26, 32, 96), (0, 0), icon.getchannel("A"))
    shadow = shadow.filter(ImageFilter.GaussianBlur(max(2, size // 34)))
    sheet.alpha_composite(shadow, (x, y + max(2, size // 22)))
    sheet.alpha_composite(icon, (x, y))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT
    return ImageFont.truetype(path, size)


def caption(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int,
            size: int = 13, colour=INK, bold: bool = False) -> None:
    face = font(size, bold)
    while face.getlength(text) > width and size > 8:
        size -= 1
        face = font(size, bold)
    draw.text((x, y), text, fill=colour, font=face, anchor="ma")


# --------------------------------------------------------------------------- #
# the sheets
# --------------------------------------------------------------------------- #

def grid(sheet: Image.Image, draw: ImageDraw.ImageDraw, entries, *, x0: int, y0: int,
         cell: int, cols: int, icon: int, label: bool = True) -> int:
    for i, (name, path) in enumerate(entries):
        col, row = i % cols, i // cols
        cx = x0 + col * cell
        cy = y0 + row * cell
        place(sheet, load(path, icon), cx + (cell - icon) // 2, cy)
        if label:
            caption(draw, name, cx + cell // 2, cy + icon + 12, cell - 12)
    rows = (len(entries) + cols - 1) // cols
    return y0 + rows * cell


def apps_sheet() -> None:
    names = [
        ("Files", "files"), ("Firefox", "firefox"), ("Google Chrome", "google-chrome"),
        ("Emacs", "emacs"), ("GIMP", "gimp"), ("VLC", "vlc-media-player"),
        ("Telegram", "telegram"), ("Terminal", "console"),
        ("Amberol", "amberol"), ("Riff", "riff"), ("Fretboard", "fretboard"),
        ("Euphonica", "euphonica"), ("Remmina", "remmina"), ("TigerVNC", "tigervnc"),
        ("Boxes", "boxes"), ("Virtual Machine Manager", "virtual-machine-manager"),
        ("Warehouse", "warehouse"), ("qBittorrent", "qbittorrent"),
        ("Mines", "mines"), ("Sudoku", "sudoku"), ("Mahjongg", "mahjongg"),
        ("Reversi", "reversi"), ("Quadrapassel", "quadrapassel"),
        ("Image Viewer", "image-viewer"), ("Extensions", "extensions"),
        ("Color Profile Viewer", "color-profile-viewer"), ("btop++", "btop"),
    ]
    entries = [(label, ROOT / "app-icons" / slug / "icon-256.png")
               for label, slug in names
               if (ROOT / "app-icons" / slug / "icon-256.png").exists()][:24]
    cols = 8
    cell, icon = 190, 148
    rows = (len(entries) + cols - 1) // cols
    sheet = background(cols * cell + 40, rows * cell + 60)
    draw = ImageDraw.Draw(sheet)
    grid(sheet, draw, entries, x0=20, y0=26, cell=cell, cols=cols, icon=icon)
    sheet.save(OUT / "apps.png", optimize=True)


def era_sheet() -> None:
    """The OS X era ensemble: the icons Leopard through Mavericks shipped."""
    records = json.loads((ROOT / "library" / "artwork.json").read_text())
    entries = [(r["name"], ROOT / "app-icons" / r["slug"] / "icon-256.png") for r in records]
    entries = [(label, path) for label, path in entries if path.exists()]
    cols = 8
    cell, icon = 190, 148
    rows = (len(entries) + cols - 1) // cols
    sheet = background(cols * cell + 40, rows * cell + 60)
    draw = ImageDraw.Draw(sheet)
    grid(sheet, draw, entries, x0=20, y0=26, cell=cell, cols=cols, icon=icon)
    sheet.save(OUT / "era.png", optimize=True)


def projects_sheet() -> None:
    names = [
        "skeu-icons", "maak", "maak-el", "sift",
        "lambdock", "araneola", "bewaking", "byggsteg", "consceal", "veritas",
        "veritas-el", "wikimusic", "symbanta", "symbanta-dashboard", "guix",
        "nixpkgs", "torikomi", "pingwing", "scriba", "lucidplan", "olive-css",
        "hygguile", "carvoeiro-water-fun", "jointhefreeworld", "heks-linux",
        "heks-emacs", "heks-bash", "heks-toon", "kracht", "skapa", "wolkenschloss", "wolk-jjba",
        "mutastructura", "lenkesamler", "private-notes", "iter-vitae",
    ]
    entries = [(n, ROOT / "project-icons" / n / "icon-256.png")
               for n in names if (ROOT / "project-icons" / n / "icon-256.png").exists()]
    cols = 9
    cell, icon = 172, 128
    rows = (len(entries) + cols - 1) // cols
    sheet = background(cols * cell + 40, rows * cell + 60)
    draw = ImageDraw.Draw(sheet)
    grid(sheet, draw, entries, x0=20, y0=22, cell=cell, cols=cols, icon=icon)
    sheet.save(OUT / "projects.png", optimize=True)


def contexts_sheet() -> None:
    theme = ROOT / "skeu-icons" / "256x256"
    rows = [
        ("categories", ["applications-development", "applications-games",
                        "applications-graphics", "applications-internet",
                        "applications-multimedia", "applications-office",
                        "applications-science", "applications-system",
                        "applications-utilities"]),
        ("places", ["user-home", "folder-blue", "folder-blue-documents",
                    "folder-blue-download", "folder-blue-pictures", "folder-blue-video",
                    "folder-brown", "folder-green", "folder-applications"]),
        ("devices", ["drive-harddisk", "drive-harddisk-usb", "computer",
                     "phone", "printer", "camera-photo", "audio-card",
                     "network-wireless", "media-optical"]),
    ]
    cols = 9
    cell, icon = 172, 132
    row_height = icon + 58
    sheet = background(cols * cell + 40, len(rows) * row_height + 34)
    draw = ImageDraw.Draw(sheet)
    y = 22
    for context, names in rows:
        draw.text((24, y), context, fill=INK, font=font(15, True))
        entries = [(n.replace("-", " "), theme / context / f"{n}.png") for n in names]
        entries = [(label, path) for label, path in entries if path.exists()]
        grid(sheet, draw, entries, x0=20, y0=y + 26, cell=cell, cols=cols, icon=icon,
             label=False)
        y += row_height
    sheet.save(OUT / "contexts.png", optimize=True)


def hero_sheet() -> None:
    """One wide banner: a shelf of six icons spanning the three sets."""
    picks = [
        ROOT / "skeu-icons" / "256x256" / "places" / "folder.png",
        ROOT / "app-icons" / "firefox" / "icon-256.png",
        ROOT / "app-icons" / "gimp" / "icon-256.png",
        ROOT / "app-icons" / "amberol" / "icon-256.png",
        ROOT / "project-icons" / "lambdock" / "icon-256.png",
        ROOT / "project-icons" / "wikimusic" / "icon-256.png",
    ]
    picks = [p for p in picks if p.exists()]
    width, height = 1600, 520
    sheet = background(width, height)
    draw = ImageDraw.Draw(sheet)
    icon = 232
    step = width // (len(picks) + 1)
    for i, path in enumerate(picks):
        place(sheet, load(path, icon), step * (i + 1) - icon // 2, (height - icon) // 2 - 10)
    sheet.save(OUT / "hero.png", optimize=True)
    # the banner is also the social preview, so keep a 2:1 copy beside it
    sheet.crop((0, 30, width, height - 30)).save(OUT / "banner.png", optimize=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for build in (hero_sheet, apps_sheet, era_sheet, projects_sheet, contexts_sheet):
        build()
        print(f"  {build.__name__.replace('_sheet', '')}: ok", file=sys.stderr)
    total = sum(p.stat().st_size for p in OUT.glob("*.png"))
    print(f"docs/: {len(list(OUT.glob('*.png')))} sheets, {total / 1e6:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
