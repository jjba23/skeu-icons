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
# the applications the pack draws
# --------------------------------------------------------------------------- #

APP_ICONS: dict[str, tuple] = {
    # --- browsers: a steel desk globe, one enamelled band for the brand
    "Firefox": (D.browser_globe, dict(hue=24)),
    "Brave": (D.browser_globe, dict(hue=2)),
    "Google Chrome": (D.browser_globe, dict(hue=48)),
    "Zen Browser": (D.browser_globe, dict(hue=156)),
    "Nyxt": (D.browser_globe, dict(hue=188)),
    "Web": (D.browser_globe, dict(hue=205)),
    # --- terminals: a CRT shell with the prompt lit in the glass
    # One machine per emulator: the phosphor, the case tint and the nameplate on
    # the chin are the same accent, so ten terminals are ten pictures and still
    # read as one family.
    "Alacritty": (D.terminal, dict(hue=190)),
    "kitty": (D.terminal, dict(hue=210)),
    "WezTerm": (D.terminal, dict(hue=250)),
    "Console": (D.terminal, dict(hue=208)),
    "Rofi": (D.terminal, dict(hue=206, light=0.72)),
    # the theme selector is not a launcher: it is a palette of themes, so it
    # gets the palette rather than a second identical CRT.
    "Rofi Theme Selector": (T.palette, dict(hue=196, sat=0.40)),
    # --- editors and IDEs: a dark glass key-cap on a milled plinth
    "Android Studio": (D.glass_keycap, dict(glyph="code", hue=150, shape="round")),
    "Android Studio Quail 3": (D.glass_keycap, dict(glyph="brackets", hue=150, shape="round")),
    "WebStorm": (D.glass_keycap, dict(glyph="code", hue=348, shape="key")),
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
    # --- databases: brass-handled card catalogues --------------------------
    # One cabinet per program, but not one photograph of the same cabinet: the
    # drawers, the wood and the cards differ (see ``card_catalog``).
    "DataGrip": (D.card_catalog, dict(hue=30, drawers=4, wood=24)),
    "sqlitebrowser": (D.card_catalog, dict(hue=200, drawers=2, wood=36)),
    "LibreOffice Base": (D.card_catalog, dict(hue=44, drawers=3, wood=18)),
    "DBeaver": (D.card_catalog, dict(hue=268, drawers=4, wood=42)),
    "Wireshark": (D.patch_panel, dict(hue=200)),
    "Wireshark - Super User Mode": (D.patch_panel, dict(hue=0)),
    "qpwgraph": (D.patch_panel, dict(hue=262)),
    "Advanced Network Configuration": (D.patch_panel, dict(hue=30)),
    "Bluetooth Manager": (T.dongle, dict(hue=210)),
    "Bluetooth Adapters": (T.dongle, dict(hue=166)),
    "Connections": (O.router, dict(hue=196)),
    "LM-Studio": (O.chip, dict(hue=264)),
    # --- remote desktops: a display on a stand
    "RustDesk": (O.monitor, dict(hue=200)),
    "Remmina": (D.remote_desktop, dict(hue=196)),
    "Remote Viewer": (D.remote_desktop, dict(hue=28)),
    "TigerVNC": (D.remote_desktop, dict(hue=262)),
    "Boxes": (Pr.parcel, dict(hue=200)),
    "VirtualBox": (Pr.parcel, dict(hue=24)),
    "Virtual Machine Manager": (D.glass_cubes, dict(hue=210)),
    "VMware Workstation": (D.glass_cubes, dict(hue=268)),
    # --- packages and stores
    "Software": (D.display_case, dict(hue=150)),
    "Package Updater": (T.crate, dict(hue=32, sealed=True)),
    "Package Sources": (Pr.spec_sheet, dict(hue=150)),
    "Myrlyn": (T.crate, dict(hue=150)),
    "Myrlyn (read\u2011only)": (T.crate, dict(hue=150, sealed=True)),
    "Myrlyn (read-only)": (T.crate, dict(hue=150, sealed=True)),
    "YaST": (T.toolbox, dict(hue=150)),
    "YaST Software": (T.toolbox, dict(hue=26)),
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
    "Widget Factory": (T.type_block, dict(glyph="box", hue=200)),
    "Tour": (T.paper, dict(hue=200, printed="map")),
    "Welcome launcher": (T.service_bell, dict(hue=200)),
    "openSUSE Welcome": (T.service_bell, dict(hue=146)),
    "Logs": (T.journal, dict(hue=38)),
    "Parental Controls": (O.shield, dict(hue=206)),
    "Flatseal": (O.shield, dict(hue=258, glyph="lock")),
    "Proton VPN": (O.padlock, dict(hue=264, body="steel")),
    "KeePassXC": (T.keyring, dict(hue=206)),
    "Passwords and Keys": (T.keyring, dict(hue=32)),
    # The era's weather was a Dashboard widget, not an instrument: a square of
    # sky with the sun and a cloud in it, which is what people remember.
    "Weather": (O.weather, dict(hue=205)),
    "Volume Control": (D.volume_knob, dict(hue=200)),
    "Volume": (D.volume_knob, dict(hue=206)),
    # --- type and text
    "Characters": (T.type_block, dict(glyph="grid", hue=44)),
    "Webfont Bundler": (T.type_block, dict(glyph="feather", hue=206)),
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
    "Eyedropper": (D.paint_tin, dict(hue=188)),
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
    # A chat client is a speech bubble, so the family stays a family - but each
    # one is its own bubble: a different proportion, a different tail, a seam or
    # no seam, and one pair of bubbles for the threads.
    "Telegram": (D.paper_plane, dict(hue=200)),
    "Discord": (D.bubble, dict(hue=234, shape="oval", tail="right", stitched=False)),
    "Slack": (D.bubble, dict(hue=300, shape="wide", double=True)),
    "Zulip": (D.bubble, dict(hue=188, shape="square", tail="right")),
    "ZapZap": (D.bubble, dict(hue=132, tail="right")),
    "Dialect": (D.bubble, dict(hue=24, shape="oval", tail="left")),
    "Emblem": (D.bubble, dict(hue=350, stitched=False)),
    "Newsflash": (T.newspaper, dict(hue=200)),
    "Evolution": (D.envelope, dict(hue=200)),
    # --- files
    "Files": (D.chrome_folder, dict(hue=206)),
    # --- games
    "Steam": (O.gamepad, dict(hue=218)),
    "RetroArch": (D.cartridge, dict(hue=0)),
    "RetroDECK": (D.cartridge, dict(hue=262)),
    "RetroDECK Configurator": (D.volume_knob, dict(hue=338)),
    "Prism Launcher": (D.pickaxe, dict(hue=190)),
    "Cartridges": (D.cartridge, dict(hue=30)),
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
    "LibreOffice Math": (T.type_block, dict(glyph="atom", hue=264)),
    "Gaphor": (T.blueprint, dict(hue=206)),
    "Graphs": (Pr.chart_recorder, dict(hue=206)),
    "Decoder": (T.magnifier, dict(hue=196)),
    "Warp": (T.cable_coil, dict(hue=200)),
    "Maps": (T.paper, dict(hue=150, printed="map")),
    # --- the wider desktop -------------------------------------------------- #
    # Programs no single build machine has installed.  ROSTER below carries the
    # names each one answers to; the object and hue are chosen here so a fresh
    # install on any distribution meets artwork instead of a fallback.
    # browsers: the same steel globe, one enamel band per brand
    "Chromium": (D.browser_globe, dict(hue=212)),
    "Microsoft Edge": (D.browser_globe, dict(hue=196)),
    "Vivaldi": (D.browser_globe, dict(hue=8)),
    "Opera": (D.browser_globe, dict(hue=348)),
    "LibreWolf": (D.browser_globe, dict(hue=216)),
    "Falkon": (D.browser_globe, dict(hue=168)),
    "qutebrowser": (D.browser_globe, dict(hue=190)),
    "Tor Browser": (D.browser_globe, dict(hue=282)),
    # mail
    "Thunderbird": (D.envelope, dict(hue=210, stamp_hue=24)),
    "Geary": (D.envelope, dict(hue=40, seal=False)),
    # terminals
    "GNOME Terminal": (D.terminal, dict(hue=160)),
    "Konsole": (D.terminal, dict(hue=30)),
    "Xfce Terminal": (D.terminal, dict(hue=40)),
    "Terminator": (D.terminal, dict(hue=4)),
    "Tilix": (D.terminal, dict(hue=96)),
    "foot": (D.terminal, dict(hue=280)),
    "Ghostty": (D.terminal, dict(hue=310)),
    # editors and IDEs
    "Visual Studio Code": (D.glass_keycap, dict(glyph="code", hue=206, shape="wide")),
    "VSCodium": (D.glass_keycap, dict(glyph="brackets", hue=196, shape="wide")),
    "Eclipse": (D.glass_keycap, dict(glyph="brackets", hue=268, shape="round")),
    "Spyder": (D.glass_keycap, dict(glyph="wave", hue=20, shape="wide")),
    "Kate": (D.glass_keycap, dict(glyph="prompt", hue=216)),
    "Neovide": (D.glass_keycap, dict(glyph="prompt", hue=142, tone="ivory")),
    "gedit": (D.notes_pad, dict(hue=34)),
    "RStudio": (Pr.chart_recorder, dict(hue=200)),
    "Arduino IDE": (O.chip, dict(hue=188)),
    "Godot": (D.wire_cube, dict(hue=200)),
    "Unity Hub": (D.glass_cubes, dict(hue=260)),
    # files and transfer
    "Dolphin": (D.chrome_folder, dict(hue=202)),
    "Thunar": (D.chrome_folder, dict(hue=28)),
    "Nemo": (D.chrome_folder, dict(hue=148)),
    "Caja": (D.chrome_folder, dict(hue=96)),
    "PCManFM": (D.chrome_folder, dict(hue=210)),
    "FileZilla": (O.dual_display, dict(hue=12)),
    "File Roller": (Pr.parcel, dict(hue=40)),
    "Ark": (Pr.parcel, dict(hue=220)),
    "Nextcloud": (T.cloud_paperweight, dict(hue=205)),
    "Dropbox": (Pr.drawer, dict(hue=208)),
    "MEGA": (O.safe_dial, dict(hue=8)),
    "Bitwarden": (T.keyring, dict(hue=208)),
    # notes and reference
    "Obsidian": (O.gem_disc, dict(hue=272)),
    "Joplin": (T.journal, dict(hue=208)),
    "Logseq": (T.blueprint, dict(hue=262)),
    "Anki": (T.cards, dict(hue=205)),
    "Calibre": (D.book_open, dict(hue=205)),
    # communication
    "Element": (D.bubble, dict(hue=152, shape="round", tail="left")),
    "Microsoft Teams": (D.bubble, dict(hue=262, shape="square", tail="right")),
    "Mattermost": (D.bubble, dict(hue=200, shape="oval", tail="right")),
    "Rocket.Chat": (D.bubble, dict(hue=348, shape="square", tail="left")),
    "Skype": (D.bubble, dict(hue=196, shape="oval", tail="right", stitched=False)),
    "Zoom": (O.camcorder, dict(hue=205)),
    # system and packages
    "GParted": (Pr.vise, dict(hue=20)),
    "Synaptic": (T.crate, dict(hue=262)),
    "Timeshift": (T.stopwatch, dict(hue=200)),
    "Discover": (D.display_case, dict(hue=205)),
    "Docker": (T.crate, dict(hue=200)),
    "Print Settings": (O.printer, dict(hue=205)),
    # media
    "Shotcut": (D.clapper, dict(hue=24)),
    "DaVinci Resolve": (D.film_reel, dict(hue=348)),
    "Brasero": (O.optical_disc, dict(label=30)),
    "K3B": (O.optical_disc, dict(label=200)),
    "Rhythmbox": (D.record_sleeve, dict(hue=14)),
    "Elisa": (D.record_sleeve, dict(hue=196)),
    "Celluloid": (D.film_reel, dict(hue=200)),
    "Okular": (D.book_open, dict(hue=28)),
    "Gwenview": (D.loupe, dict(hue=200)),
    "Shotwell": (D.photo_print, dict(hue=340)),
    "darktable": (O.colorimeter, dict(hue=8)),
    "RawTherapee": (D.prism, dict(hue=20)),
    "Scribus": (Pr.drafting_compass, dict(hue=200)),
    "LMMS": (Pr.metronome, dict(hue=200)),
    "Mixxx": (D.tuning_fork, dict(hue=190)),
    # data and web work
    "Postman": (T.connector, dict(hue=24)),
    "Insomnia": (D.pipe_branch, dict(hue=262)),
    "DBeaver": (D.card_catalog, dict(hue=268)),
    "MySQL Workbench": (O.server, dict(hue=196)),
    "pgAdmin": (T.toolbox, dict(hue=212)),
    # games and machines
    "Lutris": (O.gamepad, dict(hue=274)),
    "Heroic": (O.joystick, dict(hue=208)),
    "Bottles": (Pr.bottle, dict(hue=34)),
    "Wine": (Pr.bottle, dict(hue=344)),
    "QEMU": (O.chip, dict(hue=12)),
    "Transmission": (D.magnet, dict(hue=8)),
    # office
    "AbiWord": (D.typewriter, dict(hue=40)),
    "Gnumeric": (D.ledger, dict(hue=96)),
}


# --------------------------------------------------------------------------- #
# programs that are not installed here, and the names they answer to
# --------------------------------------------------------------------------- #

#: ``{app name: (categories, names)}`` for software that is common on desktops
#: but absent from the machine that happened to build the pack.  Without this,
#: a Chromium user and a VS Code user get fallback icons while a YaST user does
#: not - which is backwards, since the first two are far more common.
ROSTER: dict[str, tuple[str, tuple[str, ...]]] = {
    "Chromium": ("Network;WebBrowser", (
        "chromium", "chromium-browser", "chromium-browser-unstable",
        "com.github.Eloston.UngoogledChromium")),
    "Microsoft Edge": ("Network;WebBrowser", (
        "microsoft-edge", "microsoft-edge-stable", "microsoft-edge-beta",
        "microsoft-edge-dev", "com.microsoft.Edge")),
    "Vivaldi": ("Network;WebBrowser", ("vivaldi", "vivaldi-stable", "vivaldi-snapshot")),
    "Opera": ("Network;WebBrowser", ("opera", "opera-stable")),
    "LibreWolf": ("Network;WebBrowser", ("librewolf", "io.gitlab.librewolf-community")),
    "Falkon": ("Network;WebBrowser", ("falkon", "org.kde.falkon")),
    "qutebrowser": ("Network;WebBrowser", ("qutebrowser", "org.qutebrowser.qutebrowser")),
    "Tor Browser": ("Network;WebBrowser", (
        "torbrowser", "tor-browser", "org.torproject.torbrowser-launcher")),
    "Thunderbird": ("Network;Email", (
        "thunderbird", "org.mozilla.Thunderbird", "betterbird",
        "eu.betterbird.Betterbird")),
    "Geary": ("Network;Email", ("geary", "org.gnome.Geary")),
    "GNOME Terminal": ("System;TerminalEmulator", (
        "gnome-terminal", "org.gnome.Terminal", "org.gnome.Ptyxis")),
    "Konsole": ("System;TerminalEmulator", ("konsole", "org.kde.konsole")),
    "Xfce Terminal": ("System;TerminalEmulator", ("xfce4-terminal", "org.xfce.Terminal")),
    "Terminator": ("System;TerminalEmulator", ("terminator",)),
    "Tilix": ("System;TerminalEmulator", ("tilix", "com.gexperts.Tilix")),
    "foot": ("System;TerminalEmulator", ("foot", "org.codeberg.dnkl.foot")),
    "Ghostty": ("System;TerminalEmulator", ("ghostty", "com.mitchellh.ghostty")),
    "Visual Studio Code": ("Development;IDE;TextEditor", (
        "code", "code-oss", "code-insiders", "com.visualstudio.code",
        "com.visualstudio.code.oss", "visual-studio-code", "vscode", "vscode-oss")),
    "VSCodium": ("Development;IDE;TextEditor", (
        "codium", "vscodium", "com.vscodium.codium", "com.vscodium.VSCodium")),
    "Eclipse": ("Development;IDE", ("eclipse", "org.eclipse.Java", "eclipse-ide")),
    "Spyder": ("Development;IDE;Science", ("spyder", "org.spyder_ide.spyder")),
    "Kate": ("Development;TextEditor", ("kate", "org.kde.kate")),
    "Neovide": ("Development;TextEditor", ("neovide", "io.neovide.neovide")),
    "gedit": ("Development;TextEditor", ("gedit", "org.gnome.gedit")),
    "RStudio": ("Development;Science", ("rstudio", "org.rstudio.RStudio")),
    "Arduino IDE": ("Development;IDE;Electronics", (
        "arduino", "arduino-ide", "cc.arduino.IDE2")),
    "Godot": ("Development;IDE", ("godot", "org.godotengine.Godot")),
    "Unity Hub": ("Development;IDE", ("unityhub", "unity-hub", "com.unity.UnityHub")),
    "Dolphin": ("System;FileManager", ("dolphin", "org.kde.dolphin")),
    "Thunar": ("System;FileManager", ("thunar", "org.xfce.thunar")),
    "Nemo": ("System;FileManager", ("nemo", "org.nemo.nemo")),
    "Caja": ("System;FileManager", ("caja", "org.mate.caja")),
    "PCManFM": ("System;FileManager", ("pcmanfm", "pcmanfm-qt", "lxqt-pcmanfm")),
    "FileZilla": ("Network;FileTransfer", (
        "filezilla", "org.filezillaproject.Filezilla")),
    "File Roller": ("Utility;Archiving", ("file-roller", "org.gnome.FileRoller")),
    "Ark": ("Utility;Archiving", ("ark", "org.kde.ark")),
    "Nextcloud": ("Network;FileTransfer", (
        "nextcloud", "com.nextcloud.desktopclient.nextcloud")),
    "Dropbox": ("Network;FileTransfer", ("dropbox", "com.dropbox.Client")),
    "MEGA": ("Network;FileTransfer", ("megasync", "mega", "nz.mega.MEGAsync")),
    "Bitwarden": ("Utility;Security", ("bitwarden", "com.bitwarden.desktop")),
    "Obsidian": ("Office;TextEditor", ("obsidian", "md.obsidian.Obsidian")),
    "Joplin": ("Office;TextEditor", ("joplin", "net.cozic.joplin_desktop",
                                     "net.cozic.joplin-desktop")),
    "Logseq": ("Office;TextEditor", ("logseq", "com.logseq.Logseq")),
    "Anki": ("Education", ("anki", "net.ankiweb.Anki")),
    "Calibre": ("Office;Viewer", ("calibre", "calibre-gui", "com.calibre_ebook.calibre")),
    "Element": ("Network;InstantMessaging", (
        "element", "element-desktop", "im.riot.Riot", "io.element.Element")),
    "Microsoft Teams": ("Network;InstantMessaging", (
        "teams", "teams-for-linux", "com.github.IsmaelMartinez.teams_for_linux",
        "com.microsoft.Teams")),
    "Mattermost": ("Network;InstantMessaging", (
        "mattermost", "MattermostDesktop", "com.mattermost.Desktop")),
    "Rocket.Chat": ("Network;InstantMessaging", (
        "rocket.chat", "rocketchat-desktop")),
    "Skype": ("Network;InstantMessaging", ("skype", "skypeforlinux", "com.skype.Client")),
    "Zoom": ("Network;VideoConference", ("zoom", "Zoom", "us.zoom.Zoom")),
    "GParted": ("System;Filesystem", ("gparted", "org.gnome.GParted")),
    "Synaptic": ("System;PackageManager", ("synaptic", "synaptic-kde")),
    "Timeshift": ("System;Utility", ("timeshift", "teejee2008.timeshift")),
    "Discover": ("System;PackageManager", ("discover", "org.kde.discover")),
    "Docker": ("Development;Utility", ("docker-desktop", "com.docker.Docker",
                                       "docker")),
    "Print Settings": ("System;Settings", ("system-config-printer",)),
    "Shotcut": ("AudioVideo;Video", ("shotcut", "org.shotcut.Shotcut")),
    "DaVinci Resolve": ("AudioVideo;Video", (
        "davinci-resolve", "com.blackmagicdesign.resolve")),
    "Brasero": ("AudioVideo;DiscBurning", ("brasero", "org.gnome.Brasero")),
    "K3B": ("AudioVideo;DiscBurning", ("k3b", "org.kde.k3b")),
    "Rhythmbox": ("AudioVideo;Audio;Player", (
        "rhythmbox", "org.gnome.Rhythmbox", "org.gnome.Rhythmbox3")),
    "Elisa": ("AudioVideo;Audio;Player", ("elisa", "org.kde.elisa")),
    "Celluloid": ("AudioVideo;Video;Player", (
        "celluloid", "io.github.celluloid_player.Celluloid")),
    "Okular": ("Office;Viewer", ("okular", "org.kde.okular")),
    "Gwenview": ("Graphics;Viewer", ("gwenview", "org.kde.gwenview")),
    "Shotwell": ("Graphics;Photography", ("shotwell", "org.gnome.Shotwell")),
    "darktable": ("Graphics;Photography", ("darktable", "org.darktable.Darktable")),
    "RawTherapee": ("Graphics;Photography", ("rawtherapee", "com.rawtherapee.RawTherapee")),
    "Scribus": ("Graphics;Office", ("scribus", "net.scribus.Scribus")),
    "LMMS": ("AudioVideo;Audio;Sequencer", ("lmms", "io.lmms.LMMS")),
    "Mixxx": ("AudioVideo;Audio;Player", ("mixxx", "org.mixxx.Mixxx")),
    "Postman": ("Development;Network", ("postman", "com.getpostman.Postman")),
    "Insomnia": ("Development;Network", ("insomnia", "rest.insomnia.Insomnia")),
    "DBeaver": ("Development;Database", (
        "dbeaver", "dbeaver-ce", "io.dbeaver.DBeaverCommunity")),
    "MySQL Workbench": ("Development;Database", ("mysql-workbench", "com.mysql.workbench")),
    "pgAdmin": ("Development;Database", ("pgadmin4", "pgadmin", "org.pgadmin.pgadmin4")),
    "Lutris": ("Game", ("lutris", "net.lutris.Lutris")),
    "Heroic": ("Game", ("heroic", "heroic-games-launcher",
                         "com.heroicgameslauncher.hgl")),
    "Bottles": ("Game;Utility", ("bottles", "com.usebottles.bottles")),
    "Wine": ("Game;Utility", ("wine", "winecfg", "org.winehq.wine")),
    "VirtualBox": ("System;Emulator", ("virtualbox", "VirtualBox",
                                       "org.virtualbox.VirtualBox")),
    "VMware Workstation": ("System;Emulator", (
        "vmware-workstation", "vmware-player", "com.vmware.WorkstationPro")),
    "QEMU": ("System;Emulator", ("qemu", "org.qemu.QEMU")),
    "Transmission": ("Network;FileTransfer", (
        "transmission", "transmission-gtk", "org.transmissionbt.Transmission")),
    "AbiWord": ("Office;WordProcessor", ("abiword", "com.abisource.AbiWord")),
    "Gnumeric": ("Office;Spreadsheet", ("gnumeric", "org.gnome.Gnumeric")),

    # --- the OS X era ensemble ---------------------------------------------- #
    # Applications people remember from Leopard through Mavericks.  Almost none
    # of them run on Linux, but a desktop dressed as OS X asks for their icons
    # (Adium and BetterZip did, so a Wine prefix or an old Mac theme finds them).
    # Their artwork is the era icon itself, from ``library/apps``; the names are
    # the bundle identifiers and the spellings a launcher or Wine uses.
    "Safari": ("Network;WebBrowser", ("safari", "com.apple.Safari")),
    "iCal": ("Office;Calendar", ("ical", "com.apple.iCal")),
    "Address Book": ("Network;ContactManager", ("address-book",
                                                "com.apple.AddressBook")),
    "QuickTime Player": ("AudioVideo;Player", ("quicktime-player", "quicktime",
                                                "com.apple.QuickTimePlayerX")),
    "iPhoto": ("Graphics;Photography", ("iphoto", "com.apple.iPhoto")),
    "iMovie": ("AudioVideo;Video", ("imovie", "com.apple.iMovieApp")),
    "GarageBand": ("AudioVideo;Audio", ("garageband", "com.apple.garageband")),
    "Pages": ("Office;WordProcessor", ("pages", "com.apple.iWork.Pages",
                                        "com.apple.Pages")),
    "Keynote": ("Office;Presentation", ("keynote", "com.apple.iWork.Keynote",
                                         "com.apple.Keynote")),
    "Aperture": ("Graphics;Photography", ("aperture", "com.apple.Aperture")),
    "Activity Monitor": ("System;Monitor", ("activity-monitor",
                                             "com.apple.ActivityMonitor")),
    "Disk Utility": ("System;Filesystem", ("disk-utility", "com.apple.DiskUtility")),
    "System Preferences": ("System;Settings", ("system-preferences",
                                                "com.apple.systempreferences")),
    "System Information": ("System;Monitor", ("system-information",
                                               "com.apple.SystemProfiler")),
    "Network Utility": ("Network;Utility", ("network-utility",
                                             "com.apple.NetworkUtility")),
    "Keychain Access": ("System;Security", ("keychain-access",
                                             "com.apple.keychainaccess")),
    "Font Book": ("Graphics;Font", ("font-book", "com.apple.FontBook")),
    "TextEdit": ("Office;TextEditor", ("textedit", "com.apple.TextEdit")),
    "Grapher": ("Education;Math", ("grapher", "com.apple.Grapher")),
    "DVD Player": ("AudioVideo;Player", ("dvd-player", "com.apple.DVDPlayer")),
    "FaceTime": ("Network;VideoConference", ("facetime", "com.apple.FaceTime")),
    "Game Center": ("Game", ("game-center", "com.apple.GameCenter")),
    "AirPort Utility": ("Network;Utility", ("airport-utility",
                                             "com.apple.airport.airportutility")),
    "Boot Camp Assistant": ("System;Utility", ("boot-camp-assistant",
                                                "com.apple.bootcampassistant")),
    "Script Editor": ("Development;Utility", ("script-editor",
                                               "com.apple.ScriptEditor2")),
    "iBooks Author": ("Office;WordProcessor", ("ibooks-author",
                                                "com.apple.iBooksAuthor")),
    "Bluetooth File Exchange": ("Network;FileTransfer",
                                ("bluetooth-file-exchange",
                                 "com.apple.BluetoothFileExchange")),
    "Audio MIDI Setup": ("AudioVideo;Audio", ("audio-midi-setup",
                                               "com.apple.audio.AudioMIDISetup")),
    "ColorSync Utility": ("Graphics;Utility", ("colorsync-utility",
                                                "com.apple.ColorSyncUtility")),
    "DigitalColor Meter": ("Graphics;Utility", ("digitalcolor-meter",
                                                 "com.apple.DigitalColorMeter")),
    "Directory Utility": ("System;Utility", ("directory-utility",
                                              "com.apple.DirectoryUtility")),
    "Grab": ("Utility", ("grab", "com.apple.Grab")),
    "Migration Assistant": ("System;Utility", ("migration-assistant",
                                                "com.apple.MigrateAssistant")),
    "Screen Sharing": ("Network;RemoteAccess", ("screen-sharing",
                                                 "com.apple.ScreenSharing")),
    "System Image Utility": ("System;Utility", ("system-image-utility",
                                                 "com.apple.SystemImageUtility")),
    "VoiceOver Utility": ("Utility;Accessibility", ("voiceover-utility",
                                                     "com.apple.VoiceOverUtility")),
    "Microsoft Word": ("Office;WordProcessor", ("microsoft-word",
                                                 "com.microsoft.Word")),
    "Microsoft Excel": ("Office;Spreadsheet", ("microsoft-excel",
                                                "com.microsoft.Excel")),
    "Microsoft PowerPoint": ("Office;Presentation", ("microsoft-powerpoint",
                                                      "com.microsoft.Powerpoint")),
    "Microsoft Outlook": ("Office;Email", ("microsoft-outlook",
                                            "com.microsoft.Outlook")),
    "Microsoft Messenger": ("Network;InstantMessaging",
                            ("microsoft-messenger", "com.microsoft.Messenger")),
    "Remote Desktop Connection": ("Network;RemoteAccess",
                                  ("remote-desktop-connection",
                                   "com.microsoft.rdc.mac")),
    "Twitter": ("Network;InstantMessaging", ("twitter",
                                              "com.twitter.twitter-mac")),
    "Facebook": ("Network;InstantMessaging", ("facebook",
                                               "com.facebook.Facebook")),
    "BetterZip": ("Utility;Archiving", ("betterzip",
                                         "com.macitbetter.betterzip")),
    "CleanMyMac": ("System;Utility", ("cleanmymac", "com.macpaw.CleanMyMac2")),
    "Adium": ("Network;InstantMessaging", ("adium", "com.adiumX.adiumX")),

    # --- the everyday Mac applications -------------------------------------- #
    # The ones a desktop dressed as OS X actually launches: the bubbles, the
    # stamp, the drive, the pad, the disc and the silver rocket.  Their artwork
    # is in ``library/apps``, so a Linux program mapped onto them (see
    # ``BORROWED`` in tools/make_theme_apps.py) and the Mac app itself answer
    # with the same picture.
    "Messages": ("Network;InstantMessaging", ("messages", "com.apple.MobileSMS",
                                              "com.apple.iChat")),
    "Mail": ("Network;Email", ("mail", "com.apple.mail", "com.apple.Mail")),
    "Disks": ("System;Filesystem", ("disks",)),
    "Finder": ("System;FileManager", ("finder", "com.apple.finder")),
    "Preview": ("Office;Viewer;Graphics", ("preview", "com.apple.Preview")),
    "Notes": ("Office;TextEditor", ("notes", "com.apple.Notes")),
    "iTunes": ("AudioVideo;Audio;Player", ("itunes", "com.apple.iTunes")),
    "Dictionary": ("Office;Dictionary;Education", ("dictionary",
                                                    "com.apple.Dictionary")),
    "Launchpad": ("System;Utility", ("launchpad", "com.apple.launchpad.launcher")),
    "Time Machine": ("System;Utility", ("time-machine",
                                         "com.apple.backup.launcher")),
    "App Store": ("System;PackageManager", ("app-store", "com.apple.AppStore")),
    "Xcode": ("Development;IDE", ("xcode", "com.apple.dt.Xcode")),

    # --- the suite and the era utilities ------------------------------------ #
    # The creative suite (Adobe CS2, and the Macromedia 8 that preceded it), a
    # disc burner, a DVD transcoder, the search hat, the Classic environment,
    # the projector cone, the robot and the blue marble.  None of these is a
    # Mac-only curiosity: a Linux program stands in for most of them - see
    # ``BORROWED`` and ``BORROWED_NAMES`` in tools/make_theme_apps.py - so an
    # image editor answers with the butterfly and a burning program with the
    # toaster.  The rest are catalogue entries, the way VoiceOver Utility and
    # Migration Assistant already are: the era icon people remember, kept so a
    # desktop dressed as OS X can resolve it.
    "Photoshop CS2": ("Graphics;RasterGraphics", (
        "photoshop", "photoshop-cs2", "com.adobe.Photoshop", "adobe-photoshop")),
    "Illustrator CS2": ("Graphics;VectorGraphics", (
        "illustrator", "illustrator-cs2", "com.adobe.illustrator",
        "adobe-illustrator")),
    "InDesign CS2": ("Graphics;Publishing", (
        "indesign", "indesign-cs2", "com.adobe.InDesign", "adobe-indesign")),
    "Dreamweaver 8": ("Development;WebDevelopment", (
        "dreamweaver", "dreamweaver-8", "com.macromedia.dreamweaver")),
    "Flash 8": ("Graphics;2DGraphics", (
        "flash", "flash-8", "flashplayer", "com.macromedia.Flash")),
    "Fireworks 8": ("Graphics;WebDevelopment", (
        "fireworks", "fireworks-8", "com.macromedia.fireworks")),
    "Roxio Toast": ("Utility;DiscBurning", ("roxio-toast", "toast")),
    "Roxio Popcorn": ("AudioVideo;Video", ("roxio-popcorn", "popcorn")),
    "Sherlock": ("Network;Utility", ("sherlock", "com.apple.Sherlock")),
    "Classic": ("System;Emulator", ("classic", "com.apple.Classic")),
    "Front Row": ("AudioVideo;TV", ("front-row", "frontrow",
                                      "com.apple.FrontRow")),
    "Automator": ("Utility;Automation", ("automator", "com.apple.Automator")),
    "Google Earth": ("Science;Geoscience", ("google-earth", "googleearth",
                                             "google-earth-pro",
                                             "com.google.GoogleEarth")),
    "LimeWire": ("Network;P2P", ("limewire", "com.limewire.LimeWire")),

    # --- the era's everyday tools ------------------------------------------ #
    # What the era put in the Dock and the Utilities folder: the desk
    # calculator, the chess set, the alarm clock, the photo booth, the printer,
    # the yellow note pad and Apple's X11.  Every one of them is also a job a
    # Linux desktop does, so the program that does it borrows the icon - the
    # calculator, the games menu's chess set, the webcam booth, the printer
    # settings, the scratch pad (see ``BORROWED``, ``EXTRA_NAMES`` and
    # ``BORROWED_NAMES`` in tools/make_theme_apps.py).  Their artwork is in
    # ``library/apps`` like the rest of the ensemble.
    "Calculator": ("Utility;Calculator", ("calculator", "com.apple.calculator")),
    "Chess": ("Game;BoardGame", ("chess", "com.apple.Chess")),
    "Clock": ("Utility;Clock", ("clock", "com.apple.clock")),
    "Photo Booth": ("AudioVideo;Recorder", ("photo-booth",
                                             "com.apple.PhotoBooth")),
    "Printer": ("System;Settings;HardwareSettings",
                ("printer", "printer-setup-utility", "com.apple.print.center",
                 "com.apple.PrintUtility")),
    "Stickies": ("Utility;TextEditor", ("stickies", "com.apple.Stickies")),
    "X11": ("System;Utility", ("x11", "org.xquartz.X11", "com.apple.x11")),

}


#: Extra spellings for artwork that already exists.  Desktops ask for the older
#: or shorter name of a program whose entry on the build machine only declared
#: the new one - ``gnome-calculator`` for a calculator, ``eog`` for the image
#: viewer - so the pack answers to both instead of to whichever it saw first.
EXTRA_NAMES: dict[str, tuple[str, ...]] = {
    "Calculator": ("gnome-calculator", "kcalc", "galculator", "qalculate-gtk",
                   "org.gnome.Calculator", "mate-calc", "xfce4-calculator"),
    "Chess": ("gnome-chess", "glchess", "pychess", "xboard", "stockfish"),
    "Clock": ("gnome-clocks", "kclock", "alarm-clock-applet"),
    "Files": ("nautilus", "org.gnome.files"),
    "Software": ("gnome-software", "snap-store", "ubuntu-software", "plasma-discover"),
    "Image Viewer": ("eog", "org.gnome.eog", "gpicview"),
    "Document Viewer": ("evince", "org.gnome.evince"),
    "Text Editor": ("gnome-text-editor", "org.gnome.TextEditor"),
    "Firefox": ("firefox-esr", "firefox-developer-edition", "org.mozilla.firefox"),
    "Google Chrome": ("google-chrome-stable", "google-chrome-beta",
                      "google-chrome-unstable", "com.google.Chrome"),
    "Brave": ("brave-browser", "brave-browser-beta", "com.brave.Browser"),
    "VLC media player": ("vlc", "org.videolan.VLC"),
    "mpv Media Player": ("mpv", "io.mpv.Mpv"),
    "Audacity": ("org.audacityteam.Audacity",),
    "GIMP": ("org.gimp.GIMP", "gimp-2.10"),
    "Blender": ("org.blender.Blender",),
    "Discord": ("com.discordapp.Discord",),
    "Signal": ("signal-desktop", "org.signal.Signal"),
    "Telegram": ("telegram-desktop", "org.telegram.desktop"),
    "Slack": ("com.slack.Slack",),
    "Spotify": ("com.spotify.Client",),
    "Steam": ("com.valvesoftware.Steam",),

    "Inkscape": ("org.inkscape.Inkscape",),
    "LibreOffice": ("libreoffice-startcenter", "org.libreoffice.LibreOffice",
                    "org.libreoffice.LibreOffice.startcenter"),
    "Krita": ("krita", "org.kde.krita"),
    "Kdenlive": ("org.kde.kdenlive",),
    "HandBrake": ("fr.handbrake.ghb",),
    "OBS Studio": ("obs", "com.obsproject.Studio"),
    "Disks": ("gnome-disks", "gnome-disk-utility", "org.gnome.DiskUtility"),
    "Disk Usage Analyzer": ("baobab", "org.gnome.baobab"),
    "Boxes": ("gnome-boxes", "org.gnome.Boxes"),
    "Tweaks": ("gnome-tweaks", "gnome-tweak-tool"),
    "Settings": ("gnome-control-center", "org.gnome.ControlCenter"),
    "System Monitor": ("gnome-system-monitor", "org.gnome.SystemMonitor"),
    "Logs": ("gnome-logs",),
    "Characters": ("gucharmap", "org.gnome.Characters"),
    "Calendar": ("gnome-calendar",),
    "Weather": ("gnome-weather",),
    "Maps": ("gnome-maps",),
    "Contacts": ("gnome-contacts",),
    "Clocks": ("gnome-clocks",),
    "Photos": ("gnome-photos", "org.gnome.Photos"),
    "Cheese": ("cheese", "org.gnome.Cheese"),
    "Document Scanner": ("simple-scan", "org.gnome.SimpleScan"),
    "Music": ("org.gnome.Music",),
    "Help": ("yelp", "org.gnome.Yelp"),
    "Package Updater": ("gpk-update-viewer", "org.gnome.PackageUpdater"),
    "Passwords and Keys": ("seahorse", "org.gnome.seahorse.Application"),
    "Virtual Machine Manager": ("virt-manager", "org.virt_manager.virt-manager"),
    "Remmina": ("org.remmina.Remmina",),
    "Wireshark": ("org.wireshark.Wireshark",),
    "KeePassXC": ("org.keepassxc.KeePassXC",),
    "Evolution": ("org.gnome.Evolution",),
    "Gramps": ("org.gramps_project.Gramps",),
    "Emacs": ("emacs", "emacsclient"),
    "Alacritty": ("org.alacritty.Alacritty",),
    "WezTerm": ("org.wezfurlong.wezterm",),
    "Gaphor": ("org.gaphor.Gaphor",),
    "Flatseal": ("com.github.tchx84.Flatseal",),
    "RetroArch": ("org.libretro.RetroArch",),
    "Prism Launcher": ("org.prismlauncher.PrismLauncher",),
    "Cartridges": ("page.kramo.Cartridges",),
    "Amberol": ("io.bassi.Amberol",),
    "Decoder": ("com.belmoussaoui.Decoder",),
    "Fragments": ("de.haeckerfelix.Fragments",),
    "Shortwave": ("de.haeckerfelix.Shortwave",),
    "Eyedropper": ("eyedropper", "com.github.finefindus.eyedropper"),
    "Curtail": ("com.github.huluti.Curtail",),
    "Newsflash": ("io.gitlab.news_flash.NewsFlash",),
    "Resources": ("net.nokyan.Resources",),
    "Valuta": ("io.github.idevecore.Valuta",),
    "Wordbook": ("dev.mufeed.Wordbook",),
    "Fretboard": ("dev.bragefuglseth.Fretboard",),
    "Riff": ("dev.diegovsky.Riff",),
    "Cantata": ("dog.unix.cantata.Cantata",),
    "Euphonica": ("io.github.htkhiem.Euphonica",),
    "Dialect": ("app.drey.Dialect",),
    "Impression": ("io.gitlab.adhami3310.Impression",),
    "Zulip": ("org.zulip.Zulip",),
    "ZapZap": ("com.rtosta.zapzap",),
    "RustDesk": ("com.rustdesk.RustDesk",),
    "Wike": ("com.github.hugolabe.Wike",),
    "Graphs": ("se.sjoerd.Graphs",),
    "Text Pieces": ("io.gitlab.liferooter.TextPieces",),
}


def roster_apps() -> list[dict]:
    """Desktop-entry-shaped records for the programs in ``ROSTER``.

    ``tools/make_app_icons.py`` unions these with what it discovers on the
    build machine, so the pack ships them on every distribution.
    """
    out = []
    for name in sorted(ROSTER):
        categories, names = ROSTER[name]
        out.append({
            "name": name,
            "display": name,
            "categories": categories,
            "comment": "",
            "exec": "",
            "icon": names[0],
            "wmclass": "",
            "desktop": f"{names[0]}.desktop",
            "desktops": [],
            "names": list(names),
            "roster": True,
        })
    return out


def extra_names(name: str) -> list[str]:
    """Additional lookup names declared for the artwork of ``name``."""
    return list(EXTRA_NAMES.get(name, ()))


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
