# The `places` context (and coloured folders)

The theme implements the **Places** part of the freedesktop icon spec — the context that carries
`folder`, `inode-directory`, `user-home`, `folder-documents`, `folder-drag-accept` and friends —
plus colour variants of the folder family and the HiDPI extension.

```
skeu-icons/16x16/places/ … 512x512/places/   one file per standard name, per size
skeu-icons/16x16@2x/places/ … 512x512@2x/    Scale=2 (nominal size stays 16 … 512)
skeu-icons/scalable/places/                  the vector layer for the base names
skeu-icons/index.theme                       Context=Places + ScaledDirectories
```

## Standard names → folder artwork

| standard name(s) | artwork |
|---|---|
| `folder`, `inode-directory`, `folder-home`, `user-home`, `folder-templates`, `folder-music` | generic folder |
| `folder-documents` | documents folder |
| `folder-download`, `folder-downloads` | downloads folder |
| `folder-desktop`, `user-desktop` | desktop folder |
| `folder-pictures` | pictures folder |
| `folder-videos` | movies folder |
| `folder-open`, `folder-drag-accept`, `folder-visiting` | open folder |
| `folder-publicshare` | public folder |
| `folder-development` | developer folder |
| `folder-saved-search`, `user-bookmarks` | smart folder |
| `folder-shared`, `folder-group` | group folder |
| `folder-remote`, `folder-sharepoint` | sharepoint folder |
| `folder-burn` | burnable folder |
| `folder-applications` | applications folder |
| `folder-library` | library folder |
| `folder-system` | system folder |
| `folder-users` | users folder |
| `folder-utilities` | utilities folder |
| `folder-sites` | sites folder |

There is no distinct artwork for *templates* and *music*, and *home* has no house icon in the pack, so
those names point at the generic folder — deliberately, not by accident.

Sizes: 16, 22, 24, 32, 48, 64, 128, 256, 512 in `Type=Fixed` directories (each with a `@2x`
twin declared under `ScaledDirectories` with `Scale=2`), plus `scalable/places` with the vector layer
declared the way Adwaita declares its scalable dirs: `Size=128`, `MinSize=8`, `MaxSize=512`,
`Type=Scalable`.

## Coloured folders — how the recolouring works

`folder-red`, `folder-teal-documents`, `folder-green-download`, `folder-blue-open` … 14 colours × 7
places (with the `-download`/`-downloads`, `-pictures`/`-picture`, `-videos`/`-video` alias pairs) =
**140 names**, at every size.

A plain hue-rotate destroys skeuomorphic art: the white specular highlight and the grey contact shadow
start drifting in hue, and the embossed glyph loses contrast. So the recolour happens in **CIELAB**:

1. convert sRGB → linear → XYZ (D65) → CIELAB;
2. keep **L\* exactly** (times a per-colour lightness scale), so every highlight, bevel and shadow
   keeps its original value — the "material" survives untouched;
3. rotate the hue by `target − mean_hue` of the icon's tinted pixels, so the *relative* hue structure
   of the artwork is preserved (a folder whose inner glyph is tinted differently keeps that
   relationship instead of being flattened to one hue);
4. weight the change by chroma (`C* < 3` untouched, `C* > 9` fully rotated). The near-neutral
   specular white, the grey rim and the drop shadow stay neutral, which is what keeps the result
   looking like paper and not like a colour filter;
5. scale chroma (1.0–2.0 per colour) to move from the pack's pastel blue into a saturated tone without
   touching lightness contrast.

Measured on the generic folder at 256 px: input `L* 75.9 / C* 16.6 / h 246°` → `folder-red`
`L* 65.9 / C* 33.2 / h 25°` (lightness scale 0.87), `folder-brown` `L* 52.9 / C* 17.4 / h 32°`,
`folder-graphite` `C* 1.7` — neutral, with the specular highlight and shadow scale untouched.

Palette (`hue`, `chroma`, `lightness`):
`red 25/2.0/0.87 · orange 48/2.0/0.90 · yellow 86/1.85/1.02 · lime 114/1.6/0.97 · green 146/1.7/0.90 ·
teal 181/1.6/0.90 · cyan 196/1.5/0.93 · blue 246/1.0/1.0 (native) · indigo 264/1.35/0.90 ·
violet 286/1.45/0.88 · magenta 316/1.5/0.88 · pink 340/1.5/0.93 · brown 32/1.05/0.70 ·
graphite 246/0.10/0.90`.

## Space: hard links, not copies

Aliases and colour aliases are the *same bytes*, and the base place icons are the *same renders* as
`apps/`. Everything identical is **hard-linked** (same inode, zero extra bytes):

* 31 base place names × 9 sizes + scalable → share inodes with the already-shipped `apps/` renders;
* `folder` = `inode-directory` = `folder-home` = `user-home` = `folder-templates` = `folder-music`;
* `folder-red-download` = `folder-red-downloads`, `folder-red-pictures` = `folder-red-picture`, …

Measured: 2373 hard links across the theme, 125 MB not duplicated.

## HiDPI

`ScaledDirectories` in `index.theme` lists `[<N>x<N>@2x/apps]` and `[<N>x<N>@2x/places]` blocks with
`Size=N`, `Scale=2`, `Type=Fixed` — nominal size stays N, actual pixels are 2N. Files come from the
exact-size directory when it exists (16@2x ← 32, 24@2x ← 48, 32@2x ← 64, 64@2x ← 128, 128@2x ← 256,
256@2x ← 512) by hard link, from the 1024 masters for 512@2x, and by Lanczos from the master for the
two sizes that have no exact double (22@2x = 44 px, 48@2x = 96 px). 3 078 files across 19
directories (nine sizes, nine @2x trees, one scalable layer).

## Verified

```
$ gtk-update-icon-cache -f -t skeu-icons
gtk-update-icon-cache: Cache file created successfully.

Gtk.IconTheme (skeu-icons): folder, inode-directory, user-home, folder-documents,
folder-download, folder-desktop, folder-open, folder-drag-accept, folder-saved-search,
folder-red, folder-teal-documents, folder-green-download, calculator   → all resolve to a file
```

Every `Directories=`/`ScaledDirectories=` entry in `index.theme` exists and carries `Size`, `Context`,
`Type` (and `Scale` for scaled dirs).

## Adding colours

The 14 colourways are catalogued in `theme-manifest.json`; `folder-*` names follow
`folder-<colour>-<place>`, so a new colour is one entry in the palette above plus its recolour run.
The context trees are rebuilt from scratch, so removing a colour or name never leaves stale files
behind.
