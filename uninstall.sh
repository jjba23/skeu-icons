#!/usr/bin/env bash
# Remove the "Skeu Icons" icon themes again.
#
#   ./uninstall.sh                  remove the current user's themes
#   sudo ./uninstall.sh --system    remove the system-wide themes
#   ./uninstall.sh --dry-run        show what would be removed, change nothing
#
# Every theme whose index.theme calls itself "Skeu Icons …" is removed, so the
# base theme and all of its accent and dark variants go together.  That is the
# only safe unit: the variants are symlink trees that resolve into the base
# theme, and a variant left behind would be a tree of dangling links.
#
# Your desktop picks a fallback icon theme automatically; nothing else is
# touched.  install.sh --uninstall runs this same script.
set -euo pipefail

dest_root="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
dry_run=0

for arg in "$@"; do
    case "$arg" in
        --system)    dest_root="/usr/share/icons" ;;
        --root=*)    dest_root="${arg#--root=}" ;;
        --dry-run)   dry_run=1 ;;
        -h|--help)   sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
        *)           printf 'error: unknown option %s (try --help)\n' "$arg" >&2; exit 2 ;;
    esac
done

if [ "$dest_root" = "/usr/share/icons" ] && [ "$(id -u)" -ne 0 ] && [ "$dry_run" -eq 0 ]; then
    echo "error: --system removes from /usr/share/icons and needs root" >&2
    exit 1
fi

refresh_cache() {
    local dir=$1
    for tool in gtk-update-icon-cache gtk4-update-icon-cache; do
        if command -v "$tool" >/dev/null 2>&1; then
            "$tool" -f -t "$dir" >/dev/null 2>&1 || true
        fi
    done
    if command -v kbuildsycoca6 >/dev/null 2>&1; then kbuildsycoca6 >/dev/null 2>&1 || true
    elif command -v kbuildsycoca5 >/dev/null 2>&1; then kbuildsycoca5 >/dev/null 2>&1 || true
    fi
}

run() {
    if [ "$dry_run" -eq 1 ]; then printf '  would: %s\n' "$*"; else "$@"; fi
}

if [ ! -d "$dest_root" ]; then
    echo "nothing to remove: $dest_root does not exist"
    exit 0
fi

# Match on the theme's own name, not on the directory name, so a hand-copied
# "Skeu Icons Copy" is removed too and an unrelated skeu-icons-ish directory is
# left alone.
removed=0
for index in "$dest_root"/*/index.theme; do
    [ -f "$index" ] || continue
    theme=$(dirname -- "$index")
    if grep -qE '^Name=Skeu Icons( |$)' "$index"; then
        echo "removing $theme"
        run rm -rf -- "$theme"
        removed=$((removed + 1))
    fi
done

if [ "$removed" -eq 0 ]; then
    echo "nothing to remove: no skeu-icons theme in $dest_root"
    exit 0
fi

run refresh_cache "$dest_root"
if [ "$dry_run" -eq 0 ]; then
    echo "done: removed $removed theme(s); pick another icon theme if your desktop has not already"
fi
