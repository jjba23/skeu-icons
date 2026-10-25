#!/usr/bin/env python3
"""Derive the "Alt" palette/material variants from the hand-authored icons.

Each alt keeps the exact construction (geometry, gloss, bevels, shadows) of its
base icon and re-materials it: gradient stops are replaced *positionally* per
gradient id, so a spec can never silently miss a recolour.  A few alts also get
a deliberate geometry tweak, listed in ``TWEAKS``.

    python3 tools/make_alt_icons.py                 # write every alt SVG
    python3 tools/make_alt_icons.py --check         # verify specs only
    python3 tools/make_alt_icons.py Emacs           # single alt

The generated files land in ``svg/`` next to their base, ready to be installed as
the matching app icon.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "svg"

# alt name -> (base icon, {gradient id: [stop colours in order]}, {literal: replacement})
SPECS: dict[str, tuple[str, dict[str, list[str]], dict[str, str]]] = {
    # Graphite body, gold script E: the "pro"/dark variant of the Emacs badge.
    "Emacs Alt": (
        "Emacs",
        {
            "face": ["#b9c3cf", "#8b97a5", "#5c6773", "#3c454f", "#262d35", "#141a20"],
            "faceShade": ["#ffffff", "#0d1115", "#0d1115", "#05080a"],
            "glyph": ["#fff6d8", "#ffe6a6", "#c69a34"],
        },
        {
            'stroke="#241033"': 'stroke="#0e1216"',
            'stroke="#1c0733"': 'stroke="#090c0f"',
            'flood-color="#2b0d4a"': 'flood-color="#231604"',
        },
    ),
    # Pearl key-cap in a graphite plinth with navy letters: inverted IntelliJ.
    "IntelliJ IDEA Alt": (
        "IntelliJ IDEA",
        {
            "tray": ["#9aa0a7", "#828990", "#666d74", "#4b5259", "#71787f", "#969ca3", "#6b7279", "#454b52"],
            "keyBody": ["#c3ccd6", "#96a1ad", "#697480"],
            "keyTop": ["#fdfeff", "#e8eef4", "#c8d1db", "#9fabb8", "#8592a0"],
            "glyphGrad": ["#22304a", "#1a2433", "#0e1724"],
            "innerRim": ["#ffffff", "#ffffff", "#4b555f"],
        },
        {
            'flood-opacity="0.75"': 'flood-opacity="0.32"',
            'flood-color="#000305"': 'flood-color="#5d6771"',
            'stroke="#3d444b" stroke-width="2"': 'stroke="#8a949e" stroke-width="2"',
        },
    ),
    # Midnight slate enamel with silver stitching: the "night" Signal bubble.
    "Signal Alt": (
        "Signal",
        {
            "bubbleFace": ["#a5bcd8", "#637e9f", "#354a66", "#1d2b3e", "#0b1320"],
            "bubbleShade": ["#ffffff", "#000a18", "#000a18", "#00050d"],
            "bevel": ["#ffffff", "#ffffff", "#ffffff", "#000814", "#00060e"],
        },
        {
            'stroke="#eaf1ff"': 'stroke="#cfdcec"',
            'flood-color="#03123c"': 'flood-color="#020a16"',
            'stroke-dasharray="40 30"': 'stroke-dasharray="28 26"',
        },
    ),
    # Pearl badge with an emerald bubble and a white handset: inverted WhatsApp.
    "WhatsApp Alt": (
        "WhatsApp",
        {
            "rim": ["#f4f4f4", "#dedede", "#b2b2b2", "#828282", "#aaaaaa", "#d2d2d2", "#f6f6f6", "#c6c6c6", "#6f6f6f"],
            "face": ["#ffffff", "#eef2f5", "#d2dae1", "#adb8c2", "#8b98a4", "#5f6b77"],
            "faceShade": ["#ffffff", "#2a333c", "#2a333c", "#141a20"],
            "bubble": ["#6ce8a2", "#2fd473", "#0f8f4a"],
            "phone": ["#ffffff", "#f4fbf7", "#dcebe2"],
        },
        {
            'stroke="#022415"': 'stroke="#1b2229"',
            'stroke="#01230f"': 'stroke="#242c34"',
            'flood-color="#05371d"': 'flood-color="#2b3540"',
            'fill="#ffffff" opacity="0.75" filter="url(#soft)"': 'fill="#ffffff" opacity="0.45" filter="url(#soft)"',
            'fill="#a8d9bd" opacity="0.22" filter="url(#soft)"': 'fill="#0a6b34" opacity="0.3" filter="url(#soft)"',
        },
    ),
    # Graphite padlock with a brass keyhole: the "steel" 1Password.
    "1Password Alt": (
        "1Password",
        {
            "shackle": ["#eef0f2", "#d4d8dc", "#a4aab0", "#70767c", "#b6bbc0", "#5b6167"],
            "enamel": ["#d3dbe4", "#a3aeb9", "#737e8a", "#4c5762", "#333c45", "#1b222a"],
            "faceShade": ["#ffffff", "#0b0f14", "#0b0f14", "#04070a"],
            "keyholeGrad": ["#fff6dc", "#f0d795", "#bf9a4a"],
        },
        {
            'stroke="#06183c"': 'stroke="#02060a"',
            'flood-color="#04122c"': 'flood-color="#06090e"',
            'stroke="#ffffff" stroke-width="6" opacity="0.75"': 'stroke="#fff3cf" stroke-width="6" opacity="0.8"',
        },
    ),
}

GRADIENT_RE = r'(<(?:linear|radial)Gradient id="%s"[^>]*>)(.*?)(</(?:linear|radial)Gradient>)'


def recolour_gradient(svg: str, gid: str, colours: list[str]) -> str:
    pattern = re.compile(GRADIENT_RE % re.escape(gid), re.S)
    match = pattern.search(svg)
    if match is None:
        raise SystemExit(f'gradient "{gid}" not found')
    head, body, tail = match.groups()
    stops = re.findall(r'stop-color="([^"]+)"', body)
    if len(stops) != len(colours):
        raise SystemExit(f'gradient "{gid}": {len(stops)} stops in source, {len(colours)} in spec')
    pending = iter(colours)
    new_body = re.sub(r'stop-color="[^"]+"', lambda _m: f'stop-color="{next(pending)}"', body)
    return svg[: match.start()] + head + new_body + tail + svg[match.end() :]


def make_alt(name: str, base: str, gradients, replacements) -> str:
    source = SVG_DIR / f"{base}.svg"
    svg = source.read_text()
    for gid, colours in gradients.items():
        svg = recolour_gradient(svg, gid, colours)
    for old, new in replacements.items():
        if old not in svg:
            raise SystemExit(f'{name}: literal not found in {source.name}: {old!r}')
        svg = svg.replace(old, new)
    svg = svg.replace(f"<title>{base}</title>", f"<title>{name}</title>")
    svg = re.sub(r"(<desc>)(.*?)(</desc>)",
                 lambda m: f"{m.group(1)}{m.group(2)} Alt variant: same construction, different materials.{m.group(3)}",
                 svg, count=1, flags=re.S)
    return svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", nargs="*", help="base icon names to regenerate (default: all)")
    parser.add_argument("--check", action="store_true", help="validate specs without writing")
    args = parser.parse_args(argv)

    wanted = set(args.base)
    written = 0
    for name, (base, gradients, replacements) in SPECS.items():
        if wanted and base not in wanted and name not in wanted:
            continue
        svg = make_alt(name, base, gradients, replacements)
        if not args.check:
            (SVG_DIR / f"{name}.svg").write_text(svg)
        print(f"  {'checked' if args.check else 'wrote'} svg/{name}.svg")
        written += 1
    print(f"{'validated' if args.check else 'done'}: {written} alt icon(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
