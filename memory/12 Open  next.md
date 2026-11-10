Back to [[Home]]

# Open / next

- Watch the first real run of `.github/workflows/build-jev-x.yml` after a push — that's the actual proof the binaries build and run.
- `install-linux.sh`'s system-package step (`sudo apt/dnf/pacman install xdotool wmctrl ...`) still needs sudo on a fresh machine — not bundled into the binary. If "zero assumptions, fully seamless" is still the bar, that's the next gap to close (e.g. vendor static builds of those tools, or have `osctl.py` degrade gracefully without them).
- No CI/release step yet to attach `dist/jev-x` / `dist/jev-x.exe` to a GitHub release automatically — currently just build-and-upload-artifact.
- `tests/` (Mac suite) not re-run to completion anywhere today; rerun on an actual Mac before trusting it.
