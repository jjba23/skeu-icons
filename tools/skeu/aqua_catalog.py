"""Which Aqua glyph draws which Adwaita symbolic name.

The key is the *base* name: the parity file in ``tools/symbolic-names.txt``
lists names with their ``-symbolic`` suffix and their ``-rtl`` spelling, and
:mod:`skeu.make_symbolic` folds those back to the base before looking here, so
``go-next-symbolic``, ``go-next-symbolic-rtl`` and ``go-next-rtl-symbolic`` all
resolve to one entry and the mirrored copies are generated, not hand-drawn.

Values are ``(glyph function, keyword arguments)``.  Families that differ only
in a level, a generation or a badge are generated in a loop, which is why a
551-name coverage list fits in a few hundred lines.
"""

from __future__ import annotations

from typing import Callable

from . import aqua as A
from . import aqua_glyphs as G
from . import aqua_objects as O

SYMBOLIC: dict[str, tuple[Callable[..., None], dict]] = {}


def _add(name: str, fn: Callable[..., None], **kwargs) -> None:
    SYMBOLIC[name] = (fn, kwargs)


def _many(names: list[str], fn: Callable[..., None], **kwargs) -> None:
    for name in names:
        _add(name, fn, **kwargs)


# --------------------------------------------------------------------------- #
# actions
# --------------------------------------------------------------------------- #

ACTIONS: dict[str, tuple[Callable[..., None], dict]] = {
    "action-unavailable": (G.action_unavailable, {}),
    "address-book-new": (G.address_book_new, {}),
    "application-exit": (G.system_log_out, {}),
    "appointment-new": (G.appointment_new, {}),
    "bookmark-new": (G.bookmark_new, {}),
    "call-start": (G.call_start, {}),
    "call-stop": (G.call_stop, {}),
    "camera-switch": (G.camera_switch, {}),
    "chat-message-new": (G.chat_message_new, {}),
    "color-select": (G.color_select, {}),
    "contact-new": (G.contact_new, {}),
    "document-edit": (G.document_edit, {}),
    "document-new": (G.document_new, {}),
    "document-open-recent": (G.document_open_recent, {}),
    "document-open": (G.document_open, {}),
    "document-page-setup": (G.document_page_setup, {}),
    "document-print-preview": (G.document_print_preview, {}),
    "document-print": (G.document_print, {}),
    "document-properties": (G.document_properties, {}),
    "document-revert": (G.document_revert, {}),
    "document-save-as": (G.document_save_as, {}),
    "document-save": (G.document_save, {}),
    "document-send": (G.document_send, {}),
    "edit-clear-all": (G.edit_clear_all, {}),
    "edit-clear": (G.edit_clear, {}),
    "edit-copy": (G.edit_copy, {}),
    "edit-cut": (G.edit_cut, {}),
    "edit-delete": (G.edit_delete, {}),
    "edit-find-replace": (G.edit_find_replace, {}),
    "edit-find": (G.edit_find, {}),
    "edit-paste": (G.edit_paste, {}),
    "edit-redo": (G.edit_redo, {}),
    "edit-select-all": (G.edit_select_all, {}),
    "edit-select": (G.edit_select, {}),
    "edit-undo": (G.edit_undo, {}),
    "error-correct": (G.error_correct, {}),
    "find-location": (G.find_location, {}),
    "folder-new": (G.folder_new, {}),
    "font-select": (G.font_select, {}),
    "format-indent-less": (G.format_indent, {"more": False}),
    "format-indent-more": (G.format_indent, {"more": True}),
    "format-justify-center": (G.format_justify, {"mode": "center"}),
    "format-justify-fill": (G.format_justify, {"mode": "fill"}),
    "format-justify-left": (G.format_justify, {"mode": "left"}),
    "format-justify-right": (G.format_justify, {"mode": "right"}),
    "format-text-bold": (G.format_text_bold, {}),
    "format-text-direction": (G.format_text_direction, {}),
    "format-text-direction-ltr": (G.format_text_direction, {"rtl": False}),
    "format-text-italic": (G.format_text_italic, {}),
    "format-text-plaintext": (G.format_text_plaintext, {}),
    "format-text-rich": (G.format_text_rich, {}),
    "format-text-strikethrough": (G.format_text_strikethrough, {}),
    "format-text-underline": (G.format_text_underline, {}),
    "go-bottom": (G.go_bottom, {}),
    "go-down": (G.go, {"angle": 90}),
    "go-first": (G.go_first, {}),
    "go-home": (G.go_home, {}),
    "go-jump": (G.go_jump, {}),
    "go-last": (G.go_last, {}),
    "go-next": (G.go, {"angle": 0}),
    "go-previous": (G.go, {"angle": 180}),
    "go-top": (G.go_top, {}),
    "go-up": (G.go, {"angle": 270}),
    "help-about": (G.help_about, {}),
    "insert-image": (G.insert_image, {}),
    "insert-link": (G.insert_link, {}),
    "insert-object": (G.insert_object, {}),
    "insert-text": (G.insert_text, {}),
    "list-add": (A.plus, {}),
    "list-remove": (A.minus, {}),
    "list-remove-all": (G.list_remove_all, {}),
    "mail-forward": (G.mail_forward, {}),
    "mail-mark-important": (G.mail_mark_important, {}),
    "mail-mark-junk": (G.mail_mark_junk, {}),
    "mail-mark-notjunk": (G.mail_mark_notjunk, {}),
    "mail-message-new": (G.mail_message_new, {}),
    "mail-reply-all": (G.mail_reply_all, {}),
    "mail-reply-sender": (G.mail_reply, {}),
    "mail-send-receive": (G.mail_send_receive, {}),
    "mail-send": (G.mail_send, {}),
    "mark-location": (G.mark_location, {}),
    "media-eject": (G.media_eject, {}),
    "media-playback-pause": (G.media_pause, {}),
    "media-playback-start": (G.media_play, {}),
    "media-playback-stop": (G.media_stop, {}),
    "media-record": (G.media_record, {}),
    "media-seek-backward": (G.media_seek, {"forward": False}),
    "media-seek-forward": (G.media_seek, {}),
    "media-skip-backward": (G.media_skip, {"forward": False}),
    "media-skip-forward": (G.media_skip, {}),
    "media-view-subtitles": (G.media_view_subtitles, {}),
    "object-flip-horizontal": (G.object_flip_horizontal, {}),
    "object-flip-vertical": (G.object_flip_vertical, {}),
    "object-rotate-left": (G.object_rotate_left, {}),
    "object-rotate-right": (G.object_rotate_right, {}),
    "object-select": (G.object_select, {}),
    "open-menu": (G.open_menu, {}),
    "process-stop": (G.process_stop, {}),
    "selection-mode": (G.selection_mode, {}),
    "send-to": (G.send_to, {}),
    "sidebar-show": (G.sidebar_show, {}),
    "sidebar-show-right": (G.sidebar_show_right, {}),
    "star-new": (G.star_new, {}),
    "system-log-out": (G.system_log_out, {}),
    "system-reboot": (G.system_reboot, {}),
    "system-run": (G.system_run, {}),
    "system-search": (G.system_search, {}),
    "system-shutdown": (G.system_shutdown, {}),
    "system-switch-user": (G.system_switch_user, {}),
    "tab-new": (G.tab_new, {}),
    "tools-check-spelling": (G.tools_check_spelling, {}),
    "value-decrease": (G.value, {"up": False}),
    "value-increase": (G.value, {"up": True}),
    "view-app-grid": (G.view_app_grid, {}),
    "view-conceal": (G.view_conceal, {}),
    "view-continuous": (G.view_continuous, {}),
    "view-dual": (G.view_dual, {}),
    "view-fullscreen": (G.view_fullscreen, {}),
    "view-grid": (G.view_grid, {}),
    "view-list-bullet": (G.view_list_bullet, {}),
    "view-list-ordered": (G.view_list_ordered, {}),
    "view-list": (G.view_list, {}),
    "view-mirror": (G.view_mirror, {}),
    "view-more-horizontal": (G.view_more_horizontal, {}),
    "view-more": (G.view_more, {}),
    "view-paged": (G.view_paged, {}),
    "view-pin": (G.view_pin, {}),
    "view-refresh": (G.view_refresh, {}),
    "view-restore": (G.view_restore, {}),
    "view-reveal": (G.view_reveal, {}),
    "view-sort-ascending": (G.view_sort_ascending, {}),
    "view-sort-descending": (G.view_sort_descending, {}),
    "zoom-fit-best": (G.zoom_fit_best, {}),
    "zoom-in": (G.zoom_in, {}),
    "zoom-original": (G.zoom_original, {}),
    "zoom-out": (G.zoom_out, {}),
}
SYMBOLIC.update(ACTIONS)


# --------------------------------------------------------------------------- #
# categories
# --------------------------------------------------------------------------- #

CATEGORIES: dict[str, tuple[Callable[..., None], dict]] = {
    "applications-engineering": (O.category_mark, {"kind": "engineering"}),
    "applications-games": (O.category_mark, {"kind": "games"}),
    "applications-graphics": (O.category_mark, {"kind": "graphics"}),
    "applications-multimedia": (O.category_mark, {"kind": "multimedia"}),
    "applications-science": (O.category_mark, {"kind": "science"}),
    "applications-system": (O.category_mark, {"kind": "system"}),
    "applications-utilities": (O.category_mark, {"kind": "utilities"}),
    "emoji-activities": (O.emoji_tile, {"kind": "activities"}),
    "emoji-body": (O.emoji_tile, {"kind": "body"}),
    "emoji-flags": (O.emoji_tile, {"kind": "flags"}),
    "emoji-food": (O.emoji_tile, {"kind": "food"}),
    "emoji-nature": (O.emoji_tile, {"kind": "nature"}),
    "emoji-objects": (O.emoji_tile, {"kind": "objects"}),
    "emoji-people": (O.emoji_tile, {"kind": "people"}),
    "emoji-recent": (O.emoji_tile, {"kind": "recent"}),
    "emoji-symbols": (O.emoji_tile, {"kind": "symbols"}),
    "emoji-travel": (O.emoji_tile, {"kind": "travel"}),
    "preferences-other": (O.preferences, {"kind": "other"}),
    "preferences-system": (O.preferences, {"kind": "system"}),
    "system-help": (O.legacy_app, {"kind": "help"}),
}
SYMBOLIC.update(CATEGORIES)


# --------------------------------------------------------------------------- #
# devices
# --------------------------------------------------------------------------- #

DEVICES: dict[str, tuple[Callable[..., None], dict]] = {
    "ac-adapter": (O.ac_adapter, {}),
    "audio-card": (O.audio_card, {}),
    "audio-headphones": (O.headphones, {}),
    "audio-headset": (O.headset, {}),
    "audio-input-microphone": (O.microphone, {}),
    "audio-speakers": (O.speakers, {}),
    "auth-face": (O.face_id, {}),
    "auth-fingerprint": (O.fingerprint, {}),
    "auth-sim": (O.sim, {}),
    "auth-smartcard": (O.smartcard, {}),
    "battery": (O.battery_status, {"level": 1.0}),
    "bluetooth": (O.bluetooth_state, {}),
    "camera-photo": (O.camera_photo, {}),
    "camera-video": (O.camera_video, {}),
    "camera-web": (O.webcam, {}),
    "colorimeter-colorhug": (O.colorimeter, {}),
    "computer": (O.computer, {}),
    "computer-apple-ipad": (O.ipad, {}),
    "display-projector": (O.projector, {}),
    "drive-harddisk": (A.drive, {}),
    "drive-harddisk-ieee1394": (A.drive, {"ports": 2}),
    "drive-harddisk-solidstate": (O.drive_solid_state, {}),
    "drive-harddisk-system": (A.drive, {"vents": False}),
    "drive-harddisk-usb": (A.drive, {"ports": 1}),
    "drive-multidisk": (O.drive_multidisk, {}),
    "drive-optical": (O.drive_optical, {}),
    "drive-removable-media": (A.drive, {"vents": False}),
    "input-dialpad": (O.dialpad, {}),
    "input-gaming": (O.gamepad, {}),
    "input-keyboard": (A.keyboard, {}),
    "input-mouse": (A.mouse, {}),
    "input-tablet": (O.graphics_tablet, {}),
    "input-touchpad": (O.touchpad, {}),
    "media-flash": (O.memory_card, {}),
    "media-floppy": (O.floppy, {}),
    "media-optical": (O.optical_disc, {}),
    "media-optical-bd": (O.optical_disc, {"label": "bd"}),
    "media-optical-cd": (O.optical_disc, {"label": "cd"}),
    "media-optical-cd-audio": (O.optical_disc, {"label": "cd"}),
    "media-optical-dvd": (O.optical_disc, {"label": "dvd"}),
    "media-removable": (O.removable_media, {}),
    "media-tape": (O.tape, {}),
    "media-zip": (O.zip_disk, {}),
    "modem": (O.modem, {}),
    "multimedia-player": (O.player, {}),
    "multimedia-player-apple-ipod-touch": (O.ipod_touch, {}),
    "network-cellular": (O.network_cellular, {}),
    "network-wired": (O.network_wired, {}),
    "network-wireless": (O.network_wireless, {}),
    "pda": (O.pda, {}),
    "phone": (A.phone, {}),
    "phone-apple-iphone": (O.iphone, {}),
    "phone-old": (O.rollout_phone, {}),
    "printer": (O.printer, {}),
    "printer-network": (O.printer, {}),
    "scanner": (O.scanner, {}),
    "tablet": (A.tablet, {}),
    "thunderbolt": (O.thunderbolt, {}),
    "tv": (O.tv, {}),
    "uninterruptible-power-supply": (O.ups, {}),
    "video-display": (A.display, {}),
    "video-joined-displays": (O.joined_displays, {}),
    "video-single-display": (O.single_display, {}),
}
SYMBOLIC.update(DEVICES)


# --------------------------------------------------------------------------- #
# emotes
# --------------------------------------------------------------------------- #

EMOTES: dict[str, tuple[Callable[..., None], dict]] = {
    "emote-love": (O.face, {"extra": "heart", "eyes": "happy"}),
    "face-angel": (O.face, {"extra": "halo"}),
    "face-angry": (O.face, {"brows": "angry", "mouth": "frown"}),
    "face-confused": (O.face, {"brows": "worried", "mouth": "wave"}),
    "face-cool": (O.face, {"extra": "shades", "mouth": "smirk"}),
    "face-crying": (O.face, {"extra": "tears", "mouth": "frown"}),
    "face-devilish": (O.face, {"extra": "horns", "mouth": "smirk"}),
    "face-embarrassed": (O.face, {"extra": "blush", "mouth": "flat"}),
    "face-glasses": (O.face, {"extra": "glasses"}),
    "face-kiss": (O.face, {"eyes": "happy", "mouth": "smirk"}),
    "face-laugh": (O.face, {"eyes": "happy", "mouth": "big"}),
    "face-monkey": (O.face, {"extra": "monkey"}),
    "face-plain": (O.face, {"mouth": "flat"}),
    "face-raspberry": (O.face, {"mouth": "tongue"}),
    "face-sad": (O.face, {"brows": "worried", "mouth": "frown"}),
    "face-shutmouth": (O.face, {"mouth": "flat"}),
    "face-sick": (O.face, {"eyes": "lid", "mouth": "wave"}),
    "face-smile-big": (O.face, {"mouth": "big"}),
    "face-smile": (O.face, {}),
    "face-smirk": (O.face, {"mouth": "smirk"}),
    "face-surprise": (O.face, {"eyes": "wide", "mouth": "open"}),
    "face-tired": (O.face, {"eyes": "sleepy", "mouth": "flat"}),
    "face-uncertain": (O.face, {"brows": "worried", "mouth": "wave"}),
    "face-wink": (O.face, {"eyes": "wink"}),
    "face-worried": (O.face, {"brows": "worried", "mouth": "wave"}),
    "face-yawn": (O.face, {"eyes": "sleepy", "mouth": "yawn"}),
}
SYMBOLIC.update(EMOTES)


# --------------------------------------------------------------------------- #
# legacy
# --------------------------------------------------------------------------- #

LEGACY: dict[str, tuple[Callable[..., None], dict]] = {
    "accessories-calculator": (O.legacy_app, {"kind": "calculator"}),
    "accessories-character-map": (O.legacy_app, {"kind": "character-map"}),
    "accessories-dictionary": (O.legacy_app, {"kind": "dictionary"}),
    "accessories-text-editor": (O.legacy_app, {"kind": "text-editor"}),
    "applets-screenshooter": (O.legacy_app, {"kind": "screenshot"}),
    "battery-caution-charging": (O.battery_status, {"level": 0.14, "bolt": True}),
    "battery-empty": (O.battery_status, {"level": 0.0}),
    "battery-empty-charging": (O.battery_status, {"level": 0.04, "bolt": True}),
    "battery-full": (O.battery_status, {"level": 1.0}),
    "battery-full-charged": (O.battery_status, {"level": 1.0, "bolt": True}),
    "battery-full-charging": (O.battery_status, {"level": 1.0, "bolt": True}),
    "battery-good": (O.battery_status, {"level": 0.62}),
    "battery-good-charging": (O.battery_status, {"level": 0.62, "bolt": True}),
    "battery-low": (O.battery_status, {"level": 0.16}),
    "battery-low-charging": (O.battery_status, {"level": 0.16, "bolt": True}),
    "emblem-important": (O.legacy_app, {"kind": "emblem-important"}),
    "emblem-system": (O.legacy_app, {"kind": "emblem-system"}),
    "gnome-power-manager": (O.legacy_app, {"kind": "power-manager"}),
    "goa-panel": (O.legacy_app, {"kind": "panel"}),
    "help-browser": (O.legacy_app, {"kind": "help"}),
    "help-contents": (O.legacy_app, {"kind": "help"}),
    "help-faq": (O.legacy_app, {"kind": "help"}),
    "multimedia-volume-control": (O.legacy_app, {"kind": "volume-control"}),
    "preferences-color": (O.preferences, {"kind": "color"}),
    "preferences-desktop": (O.preferences, {"kind": "desktop"}),
    "preferences-desktop-accessibility": (O.preferences, {"kind": "accessibility"}),
    "preferences-desktop-appearance": (O.preferences, {"kind": "appearance"}),
    "preferences-desktop-apps": (O.preferences, {"kind": "apps"}),
    "preferences-desktop-display": (O.preferences, {"kind": "display"}),
    "preferences-desktop-font": (O.preferences, {"kind": "font"}),
    "preferences-desktop-keyboard": (O.preferences, {"kind": "keyboard"}),
    "preferences-desktop-keyboard-shortcuts": (O.preferences,
                                               {"kind": "keyboard-shortcuts"}),
    "preferences-desktop-locale": (O.preferences, {"kind": "locale"}),
    "preferences-desktop-multitasking": (O.preferences, {"kind": "multitasking"}),
    "preferences-desktop-remote-desktop": (O.preferences, {"kind": "remote-desktop"}),
    "preferences-desktop-screensaver": (O.preferences, {"kind": "screensaver"}),
    "preferences-desktop-wallpaper": (O.preferences, {"kind": "wallpaper"}),
    "preferences-system-details": (O.preferences, {"kind": "details"}),
    "preferences-system-devices": (O.preferences, {"kind": "devices"}),
    "preferences-system-network": (O.preferences, {"kind": "network"}),
    "preferences-system-network-proxy": (O.preferences, {"kind": "network-proxy"}),
    "preferences-system-notifications": (O.preferences, {"kind": "notifications"}),
    "preferences-system-parental-controls": (O.preferences,
                                             {"kind": "parental-controls"}),
    "preferences-system-privacy": (O.preferences, {"kind": "privacy"}),
    "preferences-system-search": (O.preferences, {"kind": "search"}),
    "preferences-system-sharing": (O.preferences, {"kind": "sharing"}),
    "preferences-system-time": (O.preferences, {"kind": "time"}),
    "system-file-manager": (O.legacy_app, {"kind": "file-manager"}),
    "system-software-install": (O.legacy_app, {"kind": "software-install"}),
    "system-users": (O.legacy_app, {"kind": "users"}),
    "text-editor": (O.legacy_app, {"kind": "text-editor"}),
    "user-info": (O.legacy_app, {"kind": "user-info"}),
    "utilities-terminal": (O.legacy_app, {"kind": "terminal"}),
    "web-browser": (O.legacy_app, {"kind": "browser"}),
}
SYMBOLIC.update(LEGACY)


# --------------------------------------------------------------------------- #
# mimetypes
# --------------------------------------------------------------------------- #

MIMETYPES: dict[str, tuple[Callable[..., None], dict]] = {
    "application-certificate": (G.mime_special, {"kind": "certificate"}),
    "application-rss+xml": (G.mime_special, {"kind": "rss"}),
    "application-x-addon": (G.mime_special, {"kind": "addon"}),
    "application-x-appliance": (G.mime_special, {"kind": "appliance"}),
    "application-x-executable": (G.mime_special, {"kind": "executable"}),
    "application-x-firmware": (O.chip, {}),
    "application-x-sharedlib": (G.mime_special, {"kind": "sharedlib"}),
    "audio-x-generic": (G.mime_generic, {"kind": "audio"}),
    "font-x-generic": (G.mime_font, {}),
    "image-x-generic": (G.mime_generic, {"kind": "image"}),
    "inode-directory": (G.mime_inode, {}),
    "package-x-generic": (G.mime_generic, {"kind": "package"}),
    "text-x-generic": (G.mime_generic, {"kind": "text"}),
    "video-x-generic": (G.mime_generic, {"kind": "video"}),
    "x-office-address-book": (G.mime_office, {"kind": "address-book"}),
    "x-office-calendar": (G.mime_office, {"kind": "calendar"}),
    "x-office-document": (G.mime_office, {"kind": "document"}),
    "x-office-drawing": (G.mime_office, {"kind": "drawing"}),
    "x-office-presentation": (G.mime_office, {"kind": "presentation"}),
    "x-office-spreadsheet": (G.mime_office, {"kind": "spreadsheet"}),
}
SYMBOLIC.update(MIMETYPES)


# --------------------------------------------------------------------------- #
# places
# --------------------------------------------------------------------------- #

PLACES: dict[str, tuple[Callable[..., None], dict]] = {
    "folder": (G.place_folder, {}),
    "folder-documents": (G.place_folder, {"emblem": "documents"}),
    "folder-download": (G.place_folder, {"emblem": "download"}),
    "folder-drag-accept": (G.place_folder, {"emblem": "drag-accept"}),
    "folder-music": (G.place_folder, {"emblem": "music"}),
    "folder-pictures": (G.place_folder, {"emblem": "pictures"}),
    "folder-projects": (G.place_folder, {"emblem": "projects"}),
    "folder-publicshare": (G.place_folder, {"emblem": "publicshare"}),
    "folder-remote": (G.place_folder, {"emblem": "remote"}),
    "folder-saved-search": (G.place_folder, {"emblem": "search"}),
    "folder-templates": (G.place_folder, {"emblem": "templates"}),
    "folder-videos": (G.place_folder, {"emblem": "videos"}),
    "network-server": (G.place_network_server, {}),
    "network-workgroup": (G.place_network_workgroup, {}),
    "start-here": (G.place_start_here, {}),
    "user-bookmarks": (G.user_bookmarks, {}),
    "user-desktop": (G.user_desktop, {}),
    "user-home": (G.user_home, {}),
    "user-trash": (G.user_trash, {}),
}
SYMBOLIC.update(PLACES)


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #

STATUS: dict[str, tuple[Callable[..., None], dict]] = {
    "airplane-mode": (O.airplane, {}),
    "airplane-mode-disabled": (O.airplane, {"off": True}),
    "alarm": (O.alarm, {}),
    "appointment-missed": (O.appointment_status, {"kind": "missed"}),
    "appointment-soon": (O.appointment_status, {"kind": "soon"}),
    "audio-volume-high": (O.volume, {"level": "high"}),
    "audio-volume-low": (O.volume, {"level": "low"}),
    "audio-volume-medium": (O.volume, {"level": "medium"}),
    "audio-volume-muted": (O.volume, {"level": "muted"}),
    "audio-volume-overamplified": (O.volume, {"level": "overamplified"}),
    "auth-sim-locked": (O.auth_sim_state, {"kind": "locked"}),
    "auth-sim-missing": (O.auth_sim_state, {"kind": "missing"}),
    "avatar-default": (O.avatar_default, {}),
    "battery-action": (O.battery_action, {}),
    "battery-caution": (O.battery_status, {"level": 0.14}),
    "battery-missing": (O.battery_missing, {}),
    "bluetooth-acquiring": (O.bluetooth_state, {"kind": "acquiring"}),
    "bluetooth-active": (O.bluetooth_state, {"kind": "active"}),
    "bluetooth-disabled": (O.bluetooth_state, {"kind": "disabled"}),
    "bluetooth-disconnected": (O.bluetooth_state, {"kind": "disconnected"}),
    "bluetooth-hardware-disabled": (O.bluetooth_state,
                                    {"kind": "hardware-disabled"}),
    "call-incoming": (G.call_start, {"angle": 135}),
    "call-missed": (G.call_stop, {}),
    "call-outgoing": (G.call_start, {"angle": -45}),
    "camera-disabled": (O.camera_photo, {}),
    "camera-hardware-disabled": (O.camera_photo, {}),
    "changes-allow": (O.changes, {"allow": True}),
    "changes-prevent": (O.changes, {"allow": False}),
    "channel-insecure": (O.channel_security, {"secure": False}),
    "channel-secure": (O.channel_security, {"secure": True}),
    "computer-fail": (O.computer_fail, {}),
    "content-loading": (O.content_loading, {}),
    "daytime-sunrise": (O.sunrise, {"rising": True}),
    "daytime-sunset": (O.sunrise, {"rising": False}),
    "dialog-error": (O.dialog, {"kind": "error"}),
    "dialog-information": (O.dialog, {"kind": "information"}),
    "dialog-password": (O.dialog, {"kind": "password"}),
    "dialog-question": (O.dialog, {"kind": "question"}),
    "dialog-warning": (O.dialog, {"kind": "warning"}),
    "display-brightness": (O.brightness, {"kind": "display"}),
    "folder-open": (G.document_open, {}),
    "folder-visiting": (G.place_folder, {"emblem": "visiting"}),
    "image-loading": (O.image_loading, {}),
    "image-missing": (O.image_missing, {}),
    "keyboard-brightness": (O.brightness, {"kind": "keyboard"}),
    "location-services-active": (O.location_services, {"active": True}),
    "location-services-disabled": (O.location_services, {"active": False}),
    "mail-attachment": (O.mail_attachment, {}),
    "mail-read": (O.mail_read, {}),
    "mail-replied": (O.mail_read, {"replied": True}),
    "mail-unread": (O.mail_read, {"unread": True}),
    "media-playlist-consecutive": (O.media_playlist, {"kind": "consecutive"}),
    "media-playlist-repeat-song": (O.media_playlist, {"kind": "repeat-song"}),
    "media-playlist-repeat": (O.media_playlist, {"kind": "repeat"}),
    "media-playlist-shuffle": (O.media_playlist, {"kind": "shuffle"}),
    "microphone-disabled": (O.microphone_sensitivity, {"level": "muted"}),
    "microphone-hardware-disabled": (O.microphone_sensitivity, {"level": "muted"}),
    "microphone-sensitivity-high": (O.microphone_sensitivity, {"level": "high"}),
    "microphone-sensitivity-low": (O.microphone_sensitivity, {"level": "low"}),
    "microphone-sensitivity-medium": (O.microphone_sensitivity, {"level": "medium"}),
    "microphone-sensitivity-muted": (O.microphone_sensitivity, {"level": "muted"}),
    "network-error": (O.network_state, {"kind": "error"}),
    "network-idle": (O.network_state, {"kind": "idle"}),
    "network-no-route": (O.network_state, {"kind": "no-route"}),
    "network-offline": (O.network_state, {"kind": "offline"}),
    "network-receive": (O.network_state, {"kind": "receive"}),
    "network-transmit-receive": (O.network_state, {"kind": "transmit-receive"}),
    "network-transmit": (O.network_state, {"kind": "transmit"}),
    "network-vpn": (O.network_state, {"kind": "vpn"}),
    "network-vpn-acquiring": (O.network_state, {"kind": "vpn"}),
    "network-vpn-disabled": (O.network_state, {"kind": "vpn"}),
    "network-vpn-disconnected": (O.network_state, {"kind": "vpn"}),
    "network-vpn-no-route": (O.network_state, {"kind": "vpn"}),
    "night-light": (O.night_light, {}),
    "night-light-disabled": (O.night_light, {"off": True}),
    "non-starred": (A.star, {"filled": False}),
    "notifications-disabled": (O.notifications_disabled, {}),
    "orientation-landscape": (O.orientation, {"kind": "landscape"}),
    "orientation-landscape-inverse": (O.orientation, {"kind": "landscape-inverse"}),
    "orientation-portrait-left": (O.orientation, {"kind": "portrait-left"}),
    "orientation-portrait-right": (O.orientation, {"kind": "portrait-right"}),
    "power-profile-balanced": (O.power_profile, {"kind": "balanced"}),
    "power-profile-performance": (O.power_profile, {"kind": "performance"}),
    "power-profile-power-saver": (O.power_profile, {"kind": "power-saver"}),
    "printer-error": (O.printer_state, {"kind": "error"}),
    "printer-printing": (O.printer_state, {"kind": "printing"}),
    "printer-warning": (O.printer_state, {"kind": "warning"}),
    "rotation-allowed": (O.rotation, {}),
    "rotation-locked": (O.rotation, {"locked": True}),
    "screen-shared": (O.screen_shared, {}),
    "security-high": (O.security, {"level": "high"}),
    "security-low": (O.security, {"level": "low"}),
    "security-medium": (O.security, {"level": "medium"}),
    "semi-starred": (A.half_star, {}),
    "software-update-available": (O.software_update, {}),
    "software-update-urgent": (O.software_update, {"urgent": True}),
    "starred": (A.star, {}),
    "system-lock-screen": (G.system_lock_screen, {}),
    "task-due": (O.task_status, {}),
    "task-past-due": (O.task_status, {"past": True}),
    "thunderbolt-acquiring": (O.thunderbolt, {}),
    "touch-disabled": (O.touch_disabled, {}),
    "touchpad-disabled": (O.touch_disabled, {}),
    "user-available": (O.user_status, {"kind": "available"}),
    "user-away": (O.user_status, {"kind": "away"}),
    "user-busy": (O.user_status, {"kind": "busy"}),
    "user-idle": (O.user_status, {"kind": "idle"}),
    "user-invisible": (O.user_status, {"kind": "invisible"}),
    "user-not-tracked": (O.user_status, {"kind": "not-tracked"}),
    "user-offline": (O.user_status, {"kind": "offline"}),
    "user-status-pending": (O.user_status, {"kind": "status-pending"}),
    "user-trash-full": (G.user_trash_full, {}),
    "view-wrapped": (G.view_wrapped, {}),
    "weather-clear": (O.sun, {}),
    "weather-clear-night": (O.moon, {}),
    "weather-few-clouds": (O.few_clouds, {}),
    "weather-few-clouds-night": (O.few_clouds, {"night": True}),
    "weather-fog": (O.fog, {}),
    "weather-overcast": (O.overcast, {}),
    "weather-severe-alert": (O.severe_alert, {}),
    "weather-showers": (O.rain, {}),
    "weather-showers-scattered": (O.rain, {"drops": 2, "scattered": True}),
    "weather-snow": (O.snow, {}),
    "weather-storm": (O.storm, {}),
    "weather-tornado": (O.tornado, {}),
    "weather-windy": (O.wind, {}),
}
SYMBOLIC.update(STATUS)


# --------------------------------------------------------------------------- #
# ui
# --------------------------------------------------------------------------- #

UI: dict[str, tuple[Callable[..., None], dict]] = {
    "checkbox": (G.checkbox, {}),
    "checkbox-checked": (G.checkbox, {"state": "on"}),
    "checkbox-mixed": (G.checkbox, {"state": "mixed"}),
    "focus-legacy-systray": (G.focus, {"kind": "windows"}),
    "focus-top-bar": (G.focus, {"kind": "top-bar"}),
    "focus-windows": (G.focus, {}),
    "list-drag-handle": (G.list_drag_handle, {}),
    "pan-down": (G.pan, {"angle": 90}),
    "pan-end": (G.pan, {"angle": 0}),
    "pan-start": (G.pan, {"angle": 180}),
    "pan-up": (G.pan, {"angle": 270}),
    "radio": (G.radio, {}),
    "radio-checked": (G.radio, {"state": "on"}),
    "radio-mixed": (G.radio, {"state": "mixed"}),
    "selection-end": (G.selection_edge, {"start": False}),
    "selection-start": (G.selection_edge, {"start": True}),
    "window-close": (G.window_close, {}),
    "window-maximize": (G.window_maximize, {}),
    "window-minimize": (G.window_minimize, {}),
    "window-new": (G.window_new, {}),
    "window-restore": (G.window_restore, {}),
}
SYMBOLIC.update(UI)


# --------------------------------------------------------------------------- #
# generated families: batteries, cells, wireless, wired
# --------------------------------------------------------------------------- #


def _battery_family() -> None:
    for percent in range(0, 101, 10):
        level = percent / 100.0
        _add(f"battery-level-{percent}", O.battery_status, level=level)
        _add(f"battery-level-{percent}-charging", O.battery_status, level=level,
             bolt=True)
        _add(f"battery-level-{percent}-plugged-in", O.battery_status, level=level,
             plug=True)
    _add("battery-level-100-charged", O.battery_status, level=1.0, bolt=True)


def _cellular_family() -> None:
    levels = {"none": 0, "weak": 1, "ok": 2, "good": 3, "excellent": 4}
    for name, strength in levels.items():
        _add(f"network-cellular-signal-{name}", O.cellular_signal,
             strength=strength)
    for generation in ("2g", "3g", "4g", "5g", "edge", "gprs", "hspa"):
        _add(f"network-cellular-{generation}", O.cellular_signal,
             strength=3, generation=generation.upper()
             if generation in ("2g", "3g", "4g", "5g") else generation[0].upper())
    _add("network-cellular-connected", O.cellular_signal, strength=4)
    _add("network-cellular-acquiring", O.cellular_signal, strength=1)
    _add("network-cellular-disabled", O.cellular_signal, strength=0, badge="off")
    _add("network-cellular-hardware-disabled", O.cellular_signal, strength=0,
         badge="off")
    _add("network-cellular-no-route", O.cellular_signal, strength=2, badge="warn")
    _add("network-cellular-offline", O.cellular_signal, strength=0, badge="off")


def _wireless_family() -> None:
    levels = {"none": 0, "weak": 1, "ok": 1, "good": 2, "excellent": 3}
    for name, strength in levels.items():
        _add(f"network-wireless-signal-{name}", O.wifi_signal, strength=strength)
    _add("network-wireless-connected", O.wifi_signal, strength=3)
    _add("network-wireless-acquiring", O.wifi_signal, strength=1)
    _add("network-wireless-disabled", O.wifi_badge, badge="off")
    _add("network-wireless-hardware-disabled", O.wifi_badge, badge="off")
    _add("network-wireless-encrypted", O.wifi_badge, badge="lock")
    _add("network-wireless-hotspot", O.wifi_badge, badge="hotspot")
    _add("network-wireless-no-route", O.wifi_badge, badge="warn")
    _add("network-wireless-offline", O.wifi_badge, badge="off")


def _wired_family() -> None:
    _add("network-wired-acquiring", O.network_wired)
    _add("network-wired-disconnected", O.network_state, kind="offline")
    _add("network-wired-no-route", O.network_state, kind="no-route")


_battery_family()
_cellular_family()
_wireless_family()
_wired_family()

#: Every context the parity file uses; kept here so a typo in a glyph table is
#: caught by ``make_symbolic.py --check`` rather than shipped.
CONTEXTS = ("actions", "categories", "devices", "emotes", "legacy",
            "mimetypes", "places", "status", "ui")
