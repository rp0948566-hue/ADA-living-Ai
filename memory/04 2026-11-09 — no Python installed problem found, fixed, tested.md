Back to [[Home]]

# 2026-11-09 — "no Python installed" problem: found, fixed, tested

**User's worry, confirmed real:** a non-technical person downloads the AI on Linux or Windows with zero Python installed → `install-linux.sh` / `install-windows.ps1` used to hard-require `python3`/`pip`. Mac was already fine (`Jev.app` is a compiled Swift binary).

**Investigated and ruled out:** rewriting the brain in Rust. `jev_x` is pure stdlib Python, ~5 small files, no heavy compute — a Rust rewrite would be large, risky, and solves nothing a packaged binary doesn't already solve. Not done, not recommended.

**`jev.py`'s `import fcntl` (line 27, Unix-only, would crash on Windows):** confirmed NOT part of this problem — it's only ever run inside `Jev.app` on macOS via `Jev.swift`, which calls the Mac's own `python3`. Left untouched, correctly out of scope. (12 `fcntl.flock()` call sites: lines 116, 894, 3420, 3436, 3472, 3481, 3497, 4227, 4437, 4797, 6628, 7770 — all file-locking, all fine on Mac.)

**Fix shipped (packaging, not a rewrite):**
1. `build-jev-x.sh` / `build-jev-x.ps1` — PyInstaller `--onefile` build of `jev_x/__main__.py` → `dist/jev-x` (Linux) / `dist\jev-x.exe` (Windows). Forces Pillow in as `--hidden-import` since osctl.py's `from PIL import ...` is lazy/inline and PyInstaller's static analysis would otherwise drop it.
2. `install-linux.sh` / `install-windows.ps1` rewritten — no longer require `python3`/`pip` to run the app. They now run `dist/jev-x[.exe]` if present, falling back to `python3 -m jev_x` only for a dev checkout that still has Python installed. System packages (`xdotool wmctrl scrot xclip libnotify-bin` etc., Linux only) are still installed via `sudo apt/dnf/pacman` in `install-linux.sh` — that part is unchanged, still needs sudo on a fresh Linux box (out of scope for "no Python" fix, which is specifically about the Python runtime, not these OS helper binaries).
3. `.github/workflows/build-jev-x.yml` — new CI job, builds on `ubuntu-latest` and `windows-latest`, smoke-tests `--doctor` prints valid capability JSON, uploads both binaries as artifacts on every push/PR.

**Verified in this sandbox (2026-11-09):**
- `python3 -m jev_x --doctor` runs clean — prints capability JSON, only fails on "no model server" (expected, no server running here).
- `python3 -m unittest tests_x.test_jev_x` — **10/10 tests pass.**
- `bash -n` clean on `install-linux.sh`, `build-jev-x.sh`, `build.sh`, `install.sh`.
- New workflow YAML parses clean (`yaml.safe_load`).

**Could NOT verify in this sandbox (no sudo, no working `python3 -m venv` — `ensurepip` missing, pip blocked by PEP 668 externally-managed-environment, `--break-system-packages` denied by sandbox safety policy):**
- Never actually ran PyInstaller here — `build-jev-x.sh`/`.ps1` are believed correct (standard PyInstaller CLI flags) but **untested end-to-end**. Confirm on a real dev machine or let the new CI job (`build-jev-x.yml`) prove it on the next push.
- `tests/` (98 files, Mac-app-targeted — native UI, screenshots, live-eval) was started via `discover -s tests` and did not finish in 120s; backgrounded, then lost when the session restarted (task `bhblzp4ou`, status: stopped, no output captured). Not expected to pass here anyway — no display, no `Jev.app`, no Swift. Needs a real Mac to run meaningfully; this repo's own CI (`checks.yml`) already runs it on `ubuntu-latest` for the non-UI parts.
- No Windows or Mac machine available here — `build-jev-x.ps1`, the resulting `.exe`, and the macOS `osctl.py` path (`screencapture`/`cliclick`/`osascript`) are unverified by direct execution; CI will cover Windows once it runs.
