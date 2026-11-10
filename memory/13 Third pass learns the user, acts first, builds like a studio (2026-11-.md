Back to [[Home]]

# Third pass: learns the user, acts first, builds like a studio (2026-11-10)

Harness stays Claude Code. OpenClaw and Hermes were not adopted: each is a whole assistant with its own memory and rules, and Jev's safety gate is a Claude Code hook.

Built and tested on Linux (139 tests pass, 26 skipped; nothing committed):
- **Hidden notes about the user** in `~/.config/jev/mind/` as Markdown (opens in Obsidian): `habits.md`, `mistakes.md`, `calm.md`, `goals.md`. Jev writes one line silently with `--note <kind> "<line>"`; the newest 5 per kind go with every request. `--notes` shows all, `--note forget <words|all>` removes. Nothing sensitive, nothing in Kid mode or with learning off.
- **Feelings and act-first rule** (`ACT_FIRST` in `jev.py`): when the user sounds panicked or stuck, short calm steps and the urgent thing first. Obvious, safe, undoable steps are done without asking. A saved rule "do X without asking" is a standing yes for X, including contacting a named person. Spending, deleting, posting and contacting others still wait otherwise.
- **Timed plugins**: `--plugin list | on <name> [minutes] | off <name>`. On for an hour by default, then off by itself, never uninstalled. File: `~/.config/jev/plugins.json`.
- **Best skill for the job**: agents load one best-matching skill; when none fits they search once and install the top result. Installing any skill or plugin always shows a card.
- **Studio build method**: Jev's own skill `jev_skills/skills/jev-build/SKILL.md` (plan, up to three questions, references, design direction with rich motion by default, `BRIEF.md` and `brief.json`, build, self-check with screenshots).
- **Phone**: `telegram_bridge.py`, a Telegram bot. Settings fields `telegramToken` and `telegramChat`. Only the paired chat is answered. Requests from the phone are read-only (`JEV_REMOTE=1`).

Not built, on purpose: switching between accounts to get past a site's free limit. Jev uses the signed-in account, says when the limit is reached and moves to another free source. References are for direction only, never copied.

Not checked: a real Telegram bot (no token here), the notes and build skill with a live model, the new Settings rows in a browser, anything on a Mac.
