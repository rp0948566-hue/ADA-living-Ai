Back to [[Home]]

# What people want — web research (2026-11-09)

Sampled Reddit (via mirrors), HN-linked posts, OpenAI forum, Cursor forum, voice-AI reports. Not every message (impossible); mirrors, vendor posts flagged as such.
| # | Demand / complaint (evidence) | Jev today | Proposal |
|---|---|---|---|
| 1 | Agents unreliable + slow — top complaint (arXiv 2604.17849, Operator reviews, HN) | verify rules in prompt | Small steps, verify each, auto-retry other method; local success log per task type |
| 2 | Agents deleting files, no undo, ignored denials (Antigravity D: wipe, Cursor, Claude Code rm -rf) | DENIED cmd list + Allow card | Deletes go to Trash; snapshot files before agent writes; voice "undo that" |
| 3 | Voice cuts user mid-sentence / won't take interruption / lag feels "confused" (OpenAI forum, r/ voice devs) | interrupt exists; Whisper end-of-speech | Smarter end-of-turn, instant barge-in, first spoken word < 1 s |
| 4 | Memory that persists — most requested (Vellum roundup, r/ posts) | `--me` facts + rules | "Where were we" resume across days; project/person context |
| 5 | Privacy, on-device, no training on chats (LocalLLaMA, HA users) | local model + Whisper + Piper possible | One "Private mode" switch, visible mic light, local-only proof |
| 6 | Smart home: "Jarvis runs the house" (r/ DIY Jarvis, HA) | none | Home Assistant connector |
| 7 | Only my voice should command it (speaker ID weak spot) | none | Voice-print owner lock |
| 8 | Disabled users: full voice control, describe screen, reminders (OpenAI forum VI post, accessibility pieces) | `--look`, hands, proactive | Accessibility mode: read screen aloud, nav by voice, med reminders |
| 9 | Proactive but not annoying (r/ dev asking) | `linux/proactive.py` budgeted nudges | More signals (important mail, meds), user-tunable |
| 10 | Failures unexplained ("Siri doesn't say what's wrong", 9to5Mac) | partial | Always say what failed + one next step |
