Back to [[Home]]

# What it is

Repo: `~/Desktop/jev ai/atticus-mac` (git, github.com/SaarthurR/atticus-mac). Voice/text assistant that drives the computer (shell, files, windows, mouse, keys, clipboard, screenshots) via a local or API LLM. Two independent brains, one repo:

| Brain | Platform | Entry | Needs Python on user's machine? |
|---|---|---|---|
| `jev.py` + `Jev.swift` | macOS only | `Jev.app` via `build.sh` | No — compiled Swift binary, `jev.py` run by whatever `python3` the Mac has |
| `jev_x/` package | Linux / Windows / macOS | `python3 -m jev_x` | **Was yes, now no** (see Packaging below) |

These two never call each other. `README-X.md`: "The original macOS app (`Jev.swift`, `jev.py`) is untouched; `jev_x/` is a separate, stdlib-only Python package."
