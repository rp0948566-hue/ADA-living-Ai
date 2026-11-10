Back to [[Home]]

# Repo map (top level of `atticus-mac/`)

```
jev.py            550 KB — Mac brain, run by Jev.swift via system python3
Jev.swift         623 KB — Mac native app, compiled by build.sh
jev_x/            cross-platform brain (agent.py, llm.py, osctl.py, tools.py, web.py, __main__.py)
linux/            older/separate Linux port — voice.py, listen.py, host.py, wm.py, hands.py, tier.py, models.py,
                   browser.py, cues.py, jev_calendar.py, jev_linux.py, panes.py, proactive.py, shot.py, sysmon.py,
                   voice_clone.py, worker.py, install.sh, bin/, ext/, native/  — NOT the same thing as jev_x/
ui/               HTML/JS for the Mac app's windows (agents.html, meeting.html, settings.html, onboarding.html, ...)
launcher/         separate Rust crate (src/, target/) — launcher binary, not the AI brain
video-research/   scratch folder, vendored PyAV/PIL libs — unrelated research, not shipped
tests/            98 files — Mac-app-targeted (native UI, screenshots, live-eval). NOT run in this sandbox (no display/Swift app here); wired to devbox.json's `test` script.
tests_x/          test_jev_x.py — stdlib-only, cross-platform, runs anywhere. 10/10 passing (verified 2026-11-09, this sandbox).
build.sh, install.sh, install-windows.ps1, install-linux.sh   — per-OS setup
build-jev-x.sh, build-jev-x.ps1   — NEW (2026-11-09): PyInstaller packaging for jev_x
.github/workflows/checks.yml      — existing CI: runs tests/, bash -n on build.sh/install.sh
.github/workflows/build-jev-x.yml — NEW (2026-11-09): builds jev-x binary on ubuntu-latest + windows-latest
devbox.json/.lock, flake.nix/.lock — Nix/devbox dev environment, macOS targets only (aarch64-darwin, x86_64-darwin)
```
