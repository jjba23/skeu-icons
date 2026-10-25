;;; skeu-icons — the tasks that rebuild what is on disk
;;;
;;; The pack is committed, so nothing here is needed to *use* it; these are the
;;; commands that redraw or re-derive something after you change the artwork.
;;; Every task is a normal Guile procedure, so it can be inspected, composed and
;;; called from a REPL:
;;;
;;;     maak --list          # everything below, with its docstring
;;;     maak build           # gallery + docs sheets, then verify
;;;     maak gallery         # just rebuild gallery.html
;;;     maak names           # link app/mimetype names after adding artwork
;;;     maak check           # index.theme, counts, gallery freshness
;;;
;;; The drawing programmes live in tools/ and need python3 with numpy and
;;; Pillow (plus inkscape for the hand-authored SVG set).  There is no venv and
;;; no external repository: each task runs one script that ships here.
;;;
;;; Copyright © Josep Bigorra <jjbigorra@gmail.com>
;;; SPDX-License-Identifier: CC-BY-SA-4.0

(define-module (maak)
  #:declarative? #t
  #:use-module (maak maak)
  ;; Only these are tasks; the helpers below stay private to the file.
  #:export (default gallery docs build icons apps names contexts projects alts
            report check mappings symbolic variants install uninstall clean))

;; ====== Constants ======

(define theme-name
  "skeu-icons")

;; ====== Helpers ======

(define (python . args)
  "Run python3 with ARGS from the pack root."
  (run (append (list "python3") args)))

(define (tool script . args)
  "Run one of the programmes in tools/ with ARGS."
  (python (string-append "tools/" script)))

(define (require-python)
  "Fail with a sentence, not a traceback, when python3 is missing."
  (unless (command-exists? "python3")
    (task-error
     "python3 is not on PATH"
     #:hint "The drawing programmes are plain Python; install python3 with numpy and Pillow.")))

;; ====== Tasks ======

(define (default)
  "List the tasks in this file."
  (list-tasks))

(define (gallery)
  "Rebuild gallery.html from the theme, app-icons/ and project-icons/."
  (tool "make_gallery.py"))

(define (symbolic)
  "Redraw the symbolic layer (646 names) and the un-suffixed scalable icons."
  (require-python)
  (tool "make_symbolic.py")
  (tool "make_plain.py"))

(define (variants)
  "Rebuild the accent and dark variant themes as symlink trees."
  (require-python)
  (tool "make_variants.py"))

(define (docs)
  "Recompose the README sheets in docs/ (hero, apps, projects, contexts)."
  (require-python)
  (tool "make_doc_images.py"))

(define (build)
  "Regenerate the gallery and the docs sheets, then verify the result."
  (gallery)
  (docs)
  (check))

(define (icons)
  "Draw the category, device and project icons (1024 px masters + PNG sets)."
  (require-python)
  (tool "render_skeu.py"))

(define (apps)
  "Draw one icon per GUI application installed on this machine (slow)."
  (require-python)
  (tool "make_app_icons.py"))

(define (names)
  "Link every app name and file-type name the desktops ask for into the theme.

Run this after adding artwork: a desktop asks for a desktop id, a WM class or a
mimetype name, never for the slug an icon is filed under, and a missing name
falls through to Adwaita.  Rebuild the variants afterwards - they inherit these
links through the base theme."
  (require-python)
  (tool "make_theme_apps.py")
  (tool "make_theme_mimes.py"))

(define (contexts)
  "Redraw just the category and device masters into generated/."
  (require-python)
  (tool "make_context_icons.py"))

(define (projects)
  "Redraw the project-icons/ set from tools/skeu/catalog.py."
  (require-python)
  (tool "make_project_icons.py"))

(define (alts)
  "Derive the Alt material variants of the hand-drawn icons into svg/."
  (require-python)
  (tool "make_alt_icons.py"))

(define (report)
  "Rescan $HOME for file extensions and rewrite FILE-TYPES.org."
  (require-python)
  (tool "report_file_types.py"))

(define (mappings)
  "Check that real files and installed programs find their artwork.

Sample file names - .zip, .tar.gz, .flac, .docx … - are handed to GIO exactly
as a file manager does, and the installed desktop entries are read the way a
launcher reads them; both chains are looked up through GTK in the light and the
dark theme, at every size, so a name that drifted shows up here instead of as
the wrong picture in a folder or a generic gear in the dock."
  (require-python)
  (tool "check_mapping.py"))

(define (check)
  "Verify index.theme, every directory, the counts, and that gallery.html is current."
  (require-python)
  (tool "check_theme.py"))

(define (install)
  "Install every theme for this user (~/.local/share/icons), then refresh the cache.

A system-wide install is the same script with --system and needs root, so it is
left to you: `sudo ./install.sh --system'."
  (run (list "./install.sh")))

(define (uninstall)
  "Remove every installed skeu-icons theme from this user's icon directory.

The system-wide removal is `sudo ./uninstall.sh --system'."
  (run (list "./uninstall.sh")))

(define (clean)
  "Remove caches and build leftovers; never touches the shipped artwork."
  (for-each
   (lambda (dir)
     (when (file-exists? dir) (delete-file-recursively dir)))
   (list "__pycache__" "tools/__pycache__" "tools/skeu/__pycache__"
         (string-append theme-name "/icon-theme.cache")))
  (display "cleaned caches\n"))
