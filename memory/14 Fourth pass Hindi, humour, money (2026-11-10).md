Back to [[Home]]

# Fourth pass: Hindi, humour, money (2026-11-10)

- Language: answers in the user's language; Hindi and English are the two main ones (mixed as the user mixes). Any other language: asks once, saves the answer as a rule. `talk_block()` in `jev.py`.
- Humour: one line, true facts (this computer's cores and RAM via `machine()`), English and Hindi references in the prompt: weak laptop, "NASA's supercomputer", "मेरी सलाह मानिए, ये मत करिए", the चिंटू के चाचा tongue-twister, "Leave the drama, sir. Focus on the money."
- Hindi voice (Linux): `linux/voice.py` picks a `hi_IN-*.onnx` voice when the text is Devanagari; `linux/install.sh` downloads `hi_IN-pratham-medium` (63 MB).
- Money: `MONEY` prompt block; `jev.py --price <symbol> [above|below <n>]` (exit 0 when true, works with Watch cmd for day-and-night alerts); `jev.py --simulate <symbol> [days] [amount]` runs 20,000 paper futures from 5 years of real daily prices (Yahoo chart feed). Agent skill `jev_skills/skills/jev-money`, also copied to the project's `.claude/skills/` for Claude Code.
- Kept out on purpose: no real trades, no "buy this" orders, no promised profit, no third-party trading skill downloaded from GitHub (none matched the Instagram claim; unknown code is not installed).
- Tests: `tests/test_mind.py` class Talk; 142 pass on Linux.
