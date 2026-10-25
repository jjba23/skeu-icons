#!/usr/bin/env python3
"""Rebuild ``gallery.html`` from the icons that are on disk.

One self-contained file - inline CSS/JS, no CDN - indexing everything the pack
ships: the six theme contexts at every size, plus the ``app-icons/`` and
``project-icons/`` sets.  Nothing is hard-coded: names come from the theme
directories and from the two ``index.json`` files, so adding an icon and
rerunning this script is all it takes to appear in the gallery.

    python3 tools/make_gallery.py            # rewrite gallery.html
    python3 tools/make_gallery.py --check    # exit 1 if gallery.html is stale
    python3 tools/make_gallery.py --out /tmp/g.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME = "skeu-icons"
OUT = ROOT / "gallery.html"

#: The symbolic layer's contexts, in gallery order.
SYMBOLIC_CONTEXTS = ("actions", "categories", "devices", "emotes", "legacy",
                     "mimetypes", "places", "status", "ui")

#: Theme contexts, in gallery order: (directory, section id, heading).
CONTEXTS = (
    ("apps", "apps", "Applications"),
    ("places", "places", "Places"),
    ("mimetypes", "mimetypes", "Mime types"),
    ("emblems", "emblems", "Emblems"),
    ("categories", "categories", "Categories"),
    ("devices", "devices", "Devices"),
)

#: Raster sizes the theme ships as bitmaps (the scalable layer is not listed).
SIZES = (16, 22, 24, 32, 48, 64, 128, 256, 512)
SET_SIZES = (16, 32, 64, 128, 256, 512)

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skeu Icons — icon pack gallery</title>
<style>
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 0 0 64px; background: #232326; color: #e9e9ec;
  font: 14px/1.45 system-ui, "Segoe UI", Inter, Roboto, Ubuntu, sans-serif;
}}
body.light {{ background: #f2f2f4; color: #22222a; }}
body.checker {{
  background-color: #2b2b2f;
  background-image: linear-gradient(45deg, #333338 25%, transparent 25%, transparent 75%, #333338 75%),
                    linear-gradient(45deg, #333338 25%, transparent 25%, transparent 75%, #333338 75%);
  background-size: 24px 24px; background-position: 0 0, 12px 12px;
}}
header {{ position: sticky; top: 0; z-index: 5; backdrop-filter: blur(10px);
  background: rgba(30,30,34,.82); border-bottom: 1px solid rgba(255,255,255,.08); }}
body.light header {{ background: rgba(246,246,248,.9); border-bottom-color: rgba(0,0,0,.1); }}
.wrap {{ max-width: 1280px; margin: 0 auto; padding: 16px 20px; }}
h1 {{ font-size: 19px; margin: 0 0 2px; font-weight: 650; letter-spacing: .2px; }}
.sub {{ font-size: 12px; opacity: .62; }}
.stats {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
.chip {{ font-size: 11.5px; padding: 3px 9px; border-radius: 999px;
  background: rgba(255,255,255,.07); border: 1px solid rgba(255,255,255,.09); }}
body.light .chip {{ background: rgba(0,0,0,.05); border-color: rgba(0,0,0,.08); }}
.chip b {{ font-weight: 650; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-top: 12px; }}
input[type=search] {{ flex: 1 1 260px; min-width: 200px; padding: 8px 11px; border-radius: 9px;
  border: 1px solid rgba(255,255,255,.12); background: rgba(0,0,0,.28); color: inherit; outline: none; }}
body.light input[type=search] {{ background: #fff; border-color: rgba(0,0,0,.15); }}
input[type=search]:focus {{ border-color: #5d8ef7; }}
.seg {{ display: inline-flex; border-radius: 9px; overflow: hidden; border: 1px solid rgba(255,255,255,.12); }}
.seg button {{ appearance: none; border: 0; background: transparent; color: inherit; padding: 6px 10px;
  font-size: 12px; cursor: pointer; }}
.seg button.on {{ background: #3f6fdc; color: #fff; }}
body.light .seg {{ border-color: rgba(0,0,0,.12); }}
main {{ max-width: 1280px; margin: 0 auto; padding: 8px 20px; }}
section {{ margin-top: 26px; }}
section h2 {{ font-size: 14px; text-transform: uppercase; letter-spacing: .09em; opacity: .55;
  margin: 0 0 12px; font-weight: 600; }}
section h2 span.count {{ opacity: .7; font-weight: 500; }}
.grid {{ display: grid; gap: 8px;
  grid-template-columns: repeat(auto-fill, minmax(calc(var(--icon) + 54px), 1fr)); }}
.card {{ display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 7px; padding: 12px 6px 10px; min-height: calc(var(--icon) + 34px);
  border-radius: 12px; border: 1px solid transparent; cursor: default; }}
.card:hover {{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.09); }}
body.light .card:hover {{ background: rgba(0,0,0,.05); border-color: rgba(0,0,0,.08); }}
.card img {{ display: none; flex: 0 0 auto; image-rendering: auto; }}
.card img.on {{ display: block; }}
body.tiny .card img.on {{ image-rendering: pixelated; }}
.ico {{ display: flex; align-items: flex-end; justify-content: center; gap: 10px;
  min-height: calc(var(--icon) + 6px); }}
body.compare .grid {{ grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }}
body.compare .ico {{ min-height: 0; }}
body.compare .ico img {{ display: block; }}
.card .name {{ font-size: 10.5px; text-align: center; word-break: break-word; opacity: .72;
  max-width: 100%; }}
.card:hover .name {{ opacity: 1; }}
.hidden {{ display: none !important; }}
footer {{ max-width: 1280px; margin: 40px auto 0; padding: 0 20px; font-size: 11.5px; opacity: .5; }}
a {{ color: #79a6ff; }}
</style>
</head>
<body class="">
<header>
  <div class="wrap">
    <h1>Skeu Icons — icon pack gallery</h1>
    <div class="sub">Skeuomorphic icons · metal, glass, paper and enamel objects</div>
    <div class="stats">{stats}</div>
    <div class="controls">
      <input id="q" type="search" placeholder="Filter by name…" autocomplete="off">
      <span class="chip">showing <b id="shown">0</b></span>
      <div class="seg">{size_buttons}<button id="compare" title="show every size side by side">all sizes</button></div>
      <span class="chip"><b id="size-label">128 px</b> · 1:1</span>
      <div class="seg"><button data-bg="dark" class="on">dark</button><button data-bg="light">light</button><button data-bg="checker">checker</button></div>
    </div>
  </div>
</header>
<main>
"""

FOOT = """</main>
<footer>
  Every icon is drawn for this pack with the relief renderer in <code>tools/skeu/</code>, or
  hand-authored as SVG; see <a href="CUSTOM-ICONS.md">CUSTOM-ICONS.md</a> and
  <a href="ICON-PROMPT.md">ICON-PROMPT.md</a>. Artwork released under
  <a href="LICENSE">CC BY-SA 4.0</a>.
</footer>
<script>window.__sizes = [{sizes}]; window.__initialSize = 128;</script>
<script>
const cards = () => Array.from(document.querySelectorAll('.card'));
const state = {{ size: window.__initialSize || 128, bg: 'dark', compare: false, query: '' }};

// the largest available bitmap that is not bigger than the requested size
function nearest(have) {{
  const smaller = have.filter(s => s <= state.size);
  return smaller.length ? Math.max(...smaller) : Math.min(...have);
}}

function applyBody() {{
  document.body.className = [
    state.bg === 'light' ? 'light' : '',
    state.bg === 'checker' ? 'checker' : '',
    !state.compare && state.size <= 32 ? 'tiny' : '',
    state.compare ? 'compare' : '',
  ].filter(Boolean).join(' ');
}}

// Every card already holds one <img> per available bitmap; switching size is just
// a class toggle, so nothing re-downloads and nothing shifts.
function applySize() {{
  document.documentElement.style.setProperty('--icon', state.size + 'px');
  cards().forEach(card => {{
    const have = (card.dataset.sizes || '').split(',').filter(Boolean).map(Number);
    const pick = have.length ? nearest(have) : state.size;
    card.dataset.shown = pick;
    card.querySelectorAll('.ico img').forEach(img => {{
      img.classList.toggle('on', state.compare || Number(img.dataset.size) === pick);
    }});
  }});
  document.querySelectorAll('.seg button[data-size]').forEach(b =>
    b.classList.toggle('on', Number(b.dataset.size) === state.size));
  const label = document.getElementById('size-label');
  if (label) label.textContent = state.compare ? 'every size, 1:1' : state.size + ' px';
  applyBody();
}}
function applyFilter() {{
  const q = state.query.trim().toLowerCase();
  let shown = 0;
  cards().forEach(card => {{
    const hit = !q || card.dataset.slug.includes(q) || card.dataset.label.toLowerCase().includes(q);
    card.classList.toggle('hidden', !hit);
    if (hit) shown++;
  }});
  document.querySelectorAll('section').forEach(section => {{
    const any = Array.from(section.querySelectorAll('.card')).some(c => !c.classList.contains('hidden'));
    section.classList.toggle('hidden', !any);
  }});
  const counter = document.getElementById('shown');
  if (counter) counter.textContent = shown;
}}
function init() {{
  const mode = document.getElementById('compare');
  document.querySelectorAll('.seg button[data-size]').forEach(b => b.addEventListener('click', () => {{
    state.size = Number(b.dataset.size);
    state.compare = false;
    if (mode) mode.classList.remove('on');
    applySize();
  }}));
  if (mode) mode.addEventListener('click', () => {{
    state.compare = !state.compare;
    mode.classList.toggle('on', state.compare);
    applySize();
  }});
  document.querySelectorAll('[data-bg]').forEach(b => b.addEventListener('click', () => {{
    state.bg = b.dataset.bg;
    document.querySelectorAll('[data-bg]').forEach(x => x.classList.toggle('on', x === b));
    applyBody();
  }}));
  const search = document.getElementById('q');
  if (search) search.addEventListener('input', () => {{ state.query = search.value; applyFilter(); }});
  applySize(); applyFilter();
}}
document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
"""


def theme_names(context: str) -> list[str]:
    """Every icon name shipped for CONTEXT, sorted, with the sizes it exists at."""
    names = sorted(p.stem for p in (ROOT / THEME / f"{max(SIZES)}x{max(SIZES)}" / context).glob("*.png"))
    return [n for n in names if any((ROOT / THEME / f"{s}x{s}" / context / f"{n}.png").is_file()
                                    for s in SIZES)]


def card(slug: str, label: str, title: str, srcs: dict[int, str], name: str) -> list[str]:
    sizes = ",".join(str(s) for s in sorted(srcs))
    slug, label, title, name = (html.escape(x, quote=True) for x in (slug, label, title, name))
    srcs = {s: html.escape(url, quote=True) for s, url in srcs.items()}
    out = [f'      <div class="card" data-slug="{slug}" data-label="{label}" '
           f'data-sizes="{sizes}" title="{title}">',
           "        <span class=\"ico\">"]
    for size in sorted(srcs):
        out.append(f'        <img data-size="{size}" src="{srcs[size]}" alt="{label}" '
                   f'width="{size}" height="{size}" loading="lazy" decoding="async">')
    out += ["        </span>", f'        <span class="name">{name}</span>', "      </div>"]
    return out


def theme_section(directory: str, section_id: str, heading: str) -> tuple[list[str], int]:
    names = theme_names(directory)
    out = [f'<section id="{section_id}">',
           f'  <h2>{heading} <span class="count">· {len(names)}</span></h2>',
           '  <div class="grid">']
    for name in names:
        srcs = {s: f"{THEME}/{s}x{s}/{directory}/{name}.png" for s in SIZES
                if (ROOT / THEME / f"{s}x{s}" / directory / f"{name}.png").is_file()}
        out += card(name, name, name, srcs, name)
    out += ["  </div>", "</section>"]
    return out, len(names)


def symbolic_section(context: str) -> tuple[list[str], int]:
    """One context of the symbolic layer: every icon is a single scalable SVG."""
    names = sorted(p.stem for p in (ROOT / THEME / "symbolic" / context).glob("*.svg"))
    out = [f'<section id="symbolic-{context}">',
           f'  <h2>Symbolic · {context} <span class="count">· {len(names)}</span></h2>',
           '  <div class="grid">']
    for name in names:
        src = f"{THEME}/symbolic/{context}/{name}.svg"
        out += card(f"symbolic-{context}-{name}", name, name,
                    {size: src for size in SIZES}, name)
    out += ["  </div>", "</section>"]
    return out, len(names)


def json_section(path: str, key: str, section_id: str, heading: str,
                 set_dir: str) -> tuple[list[str], int]:
    records = sorted(json.loads((ROOT / path).read_text())[key],
                     key=lambda r: (r.get("name") or r["slug"]).lower())
    out = [f'<section id="{section_id}">',
           f'  <h2>{heading} <span class="count">· {len(records)}</span></h2>',
           '  <div class="grid">']
    for record in records:
        slug = record["slug"]
        label = record.get("name") or record.get("display") or slug
        blurb = record.get("comment") or record.get("purpose") or ""
        srcs = {s: f"{set_dir}/{slug}/icon-{s}.png" for s in SET_SIZES
                if (ROOT / set_dir / slug / f"icon-{s}.png").is_file()}
        out += card(slug, label, f"{label} — {blurb}" if blurb else label, srcs, label)
    out += ["  </div>", "</section>"]
    return out, len(records)


def build() -> str:
    sections, counts = [], {}
    for directory, section_id, heading in CONTEXTS:
        block, n = theme_section(directory, section_id, heading)
        sections += block
        counts[heading] = n
    for context in SYMBOLIC_CONTEXTS:
        block, n = symbolic_section(context)
        sections += block
        counts[f"Symbolic · {context}"] = n
    for path, key, section_id, heading, set_dir in (
        ("app-icons/index.json", "apps", "app-icons", "Installed apps", "app-icons"),
        ("project-icons/index.json", "icons", "project-icons", "Projects", "project-icons"),
    ):
        block, n = json_section(path, key, section_id, heading, set_dir)
        sections += block
        counts[heading] = n

    total = sum(counts.values())
    chips = [f'<span class="chip"><b>{total}</b> icons</span>',
             f'<span class="chip">{len(counts)} sets</span>']
    chips += [f'<span class="chip">{heading} <b>{n}</b></span>' for heading, n in counts.items()]
    chips.append('<span class="chip">sizes <b>' + ", ".join(str(s) for s in SIZES) + "</b></span>")
    chips.append('<span class="chip">variants <b>skeu-icons-green, '
                 'skeu-icons-green-dark</b></span>')
    size_buttons = "".join(f'<button data-size="{s}">{s}</button>' for s in SIZES)

    return (HEAD.format(stats="".join(chips), size_buttons=size_buttons)
            + "\n".join(sections) + "\n"
            + FOOT.format(sizes=", ".join(str(s) for s in SIZES)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(OUT))
    parser.add_argument("--check", action="store_true",
                        help="do not write; fail if the file on disk differs")
    args = parser.parse_args(argv)

    text = build()
    target = Path(args.out)
    if args.check:
        current = target.read_text() if target.is_file() else ""
        if current != text:
            print(f"{target.name} is stale - run: python3 tools/make_gallery.py",
                  file=sys.stderr)
            return 1
        print(f"{target.name} is up to date")
        return 0

    target.write_text(text)
    print(f"wrote {target} ({len(text):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
