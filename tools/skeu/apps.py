"""What each generated app icon *is*.

One line per installed application: the physical object it becomes and the
single accent hue it carries.  There are no monograms here - an app is a
terminal, a globe, an envelope, a key-cap, a reel of film.  Colour is the
accent, never the body.

``design()`` is what ``tools/make_app_icons.py`` calls for every desktop entry it
discovers; apps without an explicit entry fall through to ``RULES`` (by
category) and then to one neutral object, so a newly installed program still
gets a considered icon instead of a letter on a disc.
"""

from __future__ import annotations

import re

from . import desk as D
from . import objects as O
from . import props as Pr
from . import toolkit as T


# --------------------------------------------------------------------------- #
# the 164 installed applications
# --------------------------------------------------------------------------- #

APP_ICONS: dict[str, tuple] = {
    # --- browsers: a steel desk globe, one enamelled band for the brand
    "Firefox": (D.browser_globe, dict(hue=24)),
    "Brave": (D.browser_globe, dict(hue=22)),
    "Google Chrome": (D.browser_globe, dict(hue=48)),
    "Zen Browser": (D.browser_globe, dict(hue=212)),
    "Nyxt": (D.browser_globe, dict(hue=188)),
    "Web": (D.browser_globe, dict(hue=205)),
    # --- terminals: a CRT shell with the prompt lit in the glass
    "Alacritty": (D.terminal, dict(hue=192)),
    "kitty": (D.terminal, dict(hue=278)),
    "WezTerm": (D.terminal, dict(hue=246)),
    "Console": (D.terminal, dict(hue=208)),
    "Rofi": (D.terminal, dict(hue=206, light=0.72)),
    "Rofi Theme Selector": (D.terminal, dict(hue=196, light=0.70)),
    # --- editors and IDEs: a dark glass key-cap on a milled plinth
    "Android Studio": (D.glass_keycap, dict(glyph="code", hue=150, shape="round")),
    "Android Studio Quail 3": (D.glass_keycap, dict(glyph="brackets", hue=150, shape="round")),
    "WebStorm": (D.glass_keycap, dict(glyph="code", hue=206, shape="wide")),
    "Microsoft Edit": (D.glass_keycap, dict(glyph="prompt", hue=205, tone="ivory")),
    "Text Pieces": (D.glass_keycap, dict(glyph="prompt", hue=40, tone="ivory")),
    "Workbench": (D.glass_keycap, dict(glyph="code", hue=200, shape="wide")),
    "dconf Editor": (D.glass_keycap, dict(glyph="sliders", hue=200, shape="round")),
    "Icon Editor": (D.glass_keycap, dict(glyph="nib", hue=262)),
    "Node Editor": (D.glass_keycap, dict(glyph="circuit", hue=200, shape="wide")),
    "Print Editor": (D.glass_keycap, dict(glyph="prompt", hue=30, tone="ivory")),
    "Binary": (D.glass_keycap, dict(glyph="code", hue=208, shape="round")),
    "GTK Demo": (D.glass_keycap, dict(glyph="grid", hue=200)),
    "Bruno": (D.glass_keycap, dict(glyph="pipe", hue=30, shape="wide")),
    "Constrict": (D.glass_keycap, dict(glyph="film", hue=196)),
    "JetBrains Toolbox": (T.toolbox, dict(hue=206)),
    "Git Gui": (D.pipe_branch, dict(hue=30)),
    # --- databases: brass-handled card catalogues
    "DataGrip": (D.card_catalog, dict(hue=30)),
    "sqlitebrowser": (D.card_catalog, dict(hue=200)),
    "LibreOffice Base": (D.card_catalog, dict(hue=44)),
    "Wireshark": (D.patch_panel, dict(hue=200)),
    "Wireshark - Super User Mode": (D.patch_panel, dict(hue=0)),
    "qpwgraph": (D.patch_panel, dict(hue=196)),
    "Advanced Network Configuration": (D.patch_panel, dict(hue=182)),
    "Bluetooth Manager": (T.dongle, dict(hue=210)),
    "Bluetooth Adapters": (T.dongle, dict(hue=200)),
    "Connections": (O.router, dict(hue=196)),
    "LM-Studio": (O.chip, dict(hue=264)),
    # --- remote desktops: a display on a stand
    "RustDesk": (O.monitor, dict(hue=200)),
    "Remmina": (D.remote_desktop, dict(hue=196)),
    "Remote Viewer": (D.remote_desktop, dict(hue=204)),
    "TigerVNC": (D.remote_desktop, dict(hue=210)),
    "Boxes": (Pr.parcel, dict(hue=200)),
    "Virtual Machine Manager": (D.glass_cubes, dict(hue=210)),
    # --- packages and stores
    "Software": (D.display_case, dict(hue=150)),
    "Package Updater": (T.crate, dict(hue=150, sealed=True)),
    "Package Sources": (D.card_catalog, dict(hue=150)),
    "Myrlyn": (T.crate, dict(hue=150)),
    "Myrlyn (read\u2011only)": (T.crate, dict(hue=150, sealed=True)),
    "Myrlyn (read-only)": (T.crate, dict(hue=150, sealed=True)),
    "YaST": (T.toolbox, dict(hue=150)),
    "YaST Software": (T.toolbox, dict(hue=142)),
    "Warehouse": (D.pallet, dict(hue=30)),
    "D\u00e9j\u00e0 Dup Backups": (O.drive, dict()),
    "Fragments": (T.funnel, dict(hue=200)),
    "qBittorrent": (D.magnet, dict(hue=206)),
    "ytDownloader": (T.funnel, dict(hue=10)),
    "Impression": (O.usb_stick, dict(hue=200)),
    # --- system monitors and disks
    "btop++": (D.oscilloscope, dict(hue=158)),
    "GNOME System Monitor": (T.gauge_cluster, dict(hue=32)),
    "System Monitor": (T.gauge_cluster, dict(hue=208)),
    "Resources": (T.gauge, dict(hue=266)),
    "Disk Usage Analyzer": (T.gauge, dict(hue=200)),
    "Disks": (O.drive, dict()),
    "Color Profile Viewer": (D.prism, dict(hue=250)),
    "Color Profile Viewer ": (D.prism, dict(hue=250)),
    "Curtail": (O.zip_disc, dict(hue=200)),
    # --- settings
    "Settings": (T.gears, dict(hue=206)),
    "Tweaks": (T.gears, dict(hue=264)),
    "Extensions": (D.puzzle_piece, dict(hue=152)),
    "Displays": (O.monitor, dict(hue=28)),
    "Switcheroo": (T.lens_turret, dict(hue=200)),
    "Widget Factory": (T.type_block, dict(hue=200)),
    "Tour": (T.paper, dict(hue=200, printed="map")),
    "Welcome launcher": (T.service_bell, dict(hue=150)),
    "openSUSE Welcome": (T.service_bell, dict(hue=146)),
    "Logs": (T.journal, dict(hue=38)),
    "Parental Controls": (O.shield, dict(hue=206)),
    "Flatseal": (O.shield, dict(hue=210)),
    "Proton VPN": (O.padlock, dict(hue=264, body="steel")),
    "KeePassXC": (T.keyring, dict(hue=206)),
    "Passwords and Keys": (T.keyring, dict(hue=32)),
    "Weather": (D.barometer, dict(hue=200)),
    "Volume Control": (D.volume_knob, dict(hue=200)),
    "Volume": (D.volume_knob, dict(hue=206)),
    # --- type and text
    "Characters": (T.type_block, dict(hue=44)),
    "Webfont Bundler": (T.type_block, dict(hue=206)),
    "Lorem": (D.notes_pad, dict(hue=44)),
    "Text Editor": (D.notes_pad, dict(hue=206)),
    # --- time, people, numbers
    "Solanum": (T.stopwatch, dict(hue=6)),
    "Clocks": (D.clock_dial, dict(hue=200)),
    "Calendar": (D.calendar_pad, dict(hue=6)),
    "Contacts": (D.address_book, dict(hue=206)),
    "Calculator": (D.desk_calculator, dict(hue=206)),
    "Valuta": (T.balance, dict(hue=44)),
    # --- graphics
    "GIMP": (D.paint_tube, dict(hue=28)),
    "Inkscape": (D.pen_nib, dict(hue=272)),
    "Krita": (D.paint_tin, dict(hue=306)),
    "Eyedropper": (D.paint_tin, dict(hue=300)),
    "Blender": (D.wire_cube, dict(hue=26)),
    "Image Viewer": (D.loupe, dict(hue=206)),
    "Photos": (D.photo_print, dict(hue=30)),
    "Camera": (O.camera, dict(hue=206)),
    "Cheese": (O.webcam, dict(hue=44)),
    "Document Scanner": (O.scanner, dict(hue=200)),
    # --- audio
    "Amberol": (D.gramophone, dict(hue=34)),
    "Cantata": (D.record_sleeve, dict(hue=200)),
    "Euphonica": (O.headphones, dict(hue=190)),
    "Music": (D.record_sleeve, dict(hue=340)),
    "Riff": (D.cassette, dict(hue=262)),
    "Spotify": (D.record_sleeve, dict(hue=132)),
    "Fretboard": (D.tuning_fork, dict(hue=30)),
    "Audacity": (O.microphone, dict(hue=206)),
    "Ardour": (O.speakers, dict(hue=12)),
    "Shortwave": (D.radio, dict(hue=32)),
    # --- video
    "Kdenlive": (D.clapper, dict(hue=206)),
    "Video Trimmer": (D.clapper, dict(hue=196)),
    "Totem": (D.film_reel, dict(hue=30)),
    "VLC media player": (D.film_reel, dict(hue=26)),
    "HandBrake": (O.tape_cartridge, dict(hue=30)),
    "mpv Media Player": (O.optical_disc, dict(label=278)),
    "OBS Studio": (O.camcorder, dict(hue=220)),
    # --- communication
    "Telegram": (D.paper_plane, dict(hue=200)),
    "Discord": (D.bubble, dict(hue=234)),
    "Slack": (D.bubble, dict(hue=300)),
    "Zulip": (D.bubble, dict(hue=188, tail="right")),
    "ZapZap": (D.bubble, dict(hue=132, tail="right")),
    "Dialect": (D.bubble, dict(hue=24)),
    "Emblem": (D.bubble, dict(hue=350, stitched=False)),
    "Newsflash": (T.newspaper, dict(hue=200)),
    "Evolution": (D.envelope, dict(hue=200)),
    # --- files
    "Files": (D.chrome_folder, dict(hue=206)),
    # --- games
    "Steam": (O.gamepad, dict(hue=218)),
    "RetroArch": (D.cartridge, dict(hue=0)),
    "RetroDECK": (D.cartridge, dict(hue=338)),
    "RetroDECK Configurator": (D.volume_knob, dict(hue=338)),
    "Prism Launcher": (D.pickaxe, dict(hue=190)),
    "Cartridges": (D.cartridge, dict(hue=262)),
    "Chess": (D.chess_knight, dict()),
    "Mahjongg": (D.mahjong_tile, dict(hue=148)),
    "Mines": (D.naval_mine, dict(hue=4)),
    "Quadrapassel": (D.tetromino, dict(hue=30)),
    "Reversi": (D.reversi_discs, dict(hue=120)),
    "Sudoku": (D.pencil_pad, dict(hue=44)),
    "Swell Foop": (D.game_tiles, dict(hue=300)),
    "Lights Off": (T.lamps, dict(hue=42)),
    # --- documents and reference
    "Help": (T.book, dict(hue=200, glyph="question", sat=0.30)),
    "Document Viewer": (D.book_open, dict(hue=30)),
    "Wordbook": (D.book_open, dict(hue=44)),
    "Wike": (T.book, dict(hue=200, glyph="globe")),
    "Gramps": (T.book, dict(hue=150, glyph="person")),
    "LibreOffice": (T.documents, dict(hue=150)),
    "LibreOffice Writer": (D.typewriter, dict(hue=206)),
    "LibreOffice Calc": (D.ledger, dict(hue=112)),
    "LibreOffice Impress": (D.slide_carousel, dict(hue=26)),
    "LibreOffice Draw": (T.palette, dict(hue=44, sat=0.28)),
    "LibreOffice Math": (T.type_block, dict(hue=264)),
    "Gaphor": (T.blueprint, dict(hue=206)),
    "Graphs": (Pr.chart_recorder, dict(hue=206)),
    "Decoder": (O.scanner, dict(hue=196)),
    "Warp": (T.cable_coil, dict(hue=200)),
    "Maps": (T.paper, dict(hue=150, printed="map")),
}


#: Last resort: an object chosen from the freedesktop category, never a monogram.
RULES: list[tuple[str, object, dict]] = [
    (r"WebBrowser", D.browser_globe, dict(hue=205)),
    (r"TerminalEmulator", D.terminal, dict(hue=200)),
    (r"AudioVideo.*Player|Player", D.film_reel, dict(hue=26)),
    (r"Recorder|Audio", D.record_sleeve, dict(hue=320)),
    (r"Video", D.clapper, dict(hue=206)),
    (r"Development|IDE|TextEditor", D.glass_keycap, dict(glyph="code", hue=208)),
    (r"Office|Spreadsheet|Presentation|WordProcessor", T.documents, dict(hue=206)),
    (r"Graphics|Photography", T.palette, dict(hue=272)),
    (r"Game", D.game_tiles, dict(hue=150)),
    (r"Security|Privacy", O.shield, dict(hue=206)),
    (r"Network", O.router, dict(hue=200)),
    (r"System|Settings|Monitor", T.gears, dict(hue=205)),
    (r"Utility", T.toolbox, dict(hue=205)),
    (r"Education|Science", T.flask, dict(hue=34)),
]

#: When a desktop entry matches nothing at all: a stack of neutral tiles.
DEFAULT = (T.tile_stack, dict(hue=205))


def design(name: str, categories: str = "", comment: str = "") -> tuple:
    """Return ``(builder, kwargs)`` for one application."""
    if name in APP_ICONS:
        return APP_ICONS[name]
    haystack = f"{categories} {name} {comment}"
    for pattern, builder, kwargs in RULES:
        if re.search(pattern, haystack, re.I):
            return builder, dict(kwargs)
    return DEFAULT[0], dict(DEFAULT[1])
