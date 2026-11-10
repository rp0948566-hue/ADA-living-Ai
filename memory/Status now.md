Back to [[Home]]

# Status now (2026-11-10)

- Code: `/home/claude/Desktop/jev ai/atticus-mac`. Not a git repo. Nothing committed.
- Tests: 145 pass on Linux (26 skipped). `tests/test_agents` has 4 old failures, not fixed.
- Brain setting right now: `haiku`, client `local`. In live checks it ignored the language, humour and briefing rules (answered English in Hindi, looked up no weather or news). Open question: switch to the full Claude model.
- Hindi voice `hi_IN-pratham-medium` is downloaded on this laptop. Clips generate; nobody has listened to them yet.
- Works on Linux only so far: daily briefing, "not now", Hindi voice pick, Telegram bridge start.
- Not built: Mac side of the new features, a Settings switch for the briefing, mail as a signal, a speaker-model owner-voice lock.
- Not checked: a real Telegram bot, the money skill and build skill with a live agent, the new Settings rows in a browser, the PyInstaller and CI build.

## GitHub (2026-11-10)
- Code is committed locally on branch `jev-ai` (commit 56bf8d5) in `atticus-mac`. Remote `jev` = https://github.com/rp0948566-hue/Jev-AI.git. Old `origin` (SaarthurR/atticus-mac) untouched.
- Target repo already has `main` (different history) plus `master`, `ADA-power-ai`, `ADA-power-Ai`, `ada-power-point`. Never force-push `main`; push only `jev-ai`.
- Left out of the commit: `video-research/`, `graphify-out/`, `launcher/target/`, `--listmonitors`, plus private files blocked by `.gitignore`.
- Push command: `cd "/home/claude/Desktop/jev ai/atticus-mac" && git push -u jev jev-ai`. The user was typing the login in the terminal (needs a personal access token, exact login `rp0948566-hue`). PUSH WORKED: branch `jev-ai` is on GitHub at commit 56bf8d5.

## Next session: start here
1. Push is done (branch `jev-ai`). Open https://github.com/rp0948566-hue/Jev-AI/tree/jev-ai to see it.
2. Decide: keep branch `jev-ai`, or replace `main`.
3. Switch Jev's brain from small local `haiku` to the full Claude model (rules for language, humour, briefing are ignored by the small one).
4. Build: Mac side of new features, Settings switch for the briefing (`briefing` pref has no row), mail as a briefing signal.
5. Check: listen to the Hindi clip, real Telegram bot, money and build skills with a live agent.
