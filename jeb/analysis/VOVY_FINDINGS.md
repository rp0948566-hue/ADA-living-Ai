# Vovy 0.5.8 (macOS arm64) — what the shipped code shows
Source: DMG decoded by hand (REA cannot list DMG children on Linux), app.asar extracted, main/preload/realtime bundles read with REA + grep. Static only: nothing was executed. Paraphrased; no code copied.

## Observed
- Electron app (bundle id ai.vovy.desktop). Deps: nut-js (mouse/keyboard), node-pty (terminal), playwright-core (browser), Sentry; a native accessibility helper `vovy-ax`. Permissions asked: microphone, screen capture, Apple Events.
- Voice layer = OpenAI Realtime API over WebRTC, server VAD. A separate "read this line aloud verbatim" mode lets a different brain write the text and the voice model only speak it (voice and planning are separate).
- Timing constants: speech onset 120 ms, end-of-speech hang 1300 ms, no-speech abort 6 s, max turn 30 s, idle 30 s (linger up to 5 min).
- **Conversation window**: after it speaks, the mic reopens for 8 s with a strict VAD threshold (0.7) and 300 ms pre-roll, so follow-ups need no button. It will not open while its own speech is in flight.
- Voice prompt rules (paraphrased): answer from the user's own world first; live facts are fetched fresh, memory only says where to look; a spoken promise ("on it", "opening it") must come with a real tool call in the same turn; corrections keep the original goal; garbled words are resolved from what is on screen; reply in the user's language; never use filler status lines ("Got it", "On it", "Let me think"); short follow-ups resolve from the latest turn. Context arrives as labelled items [now], [session memory], [screen] and is treated as data, not instructions.
- Real work goes to a `start_task` tool -> background tasks with a mailbox for questions/answers; the voice keeps talking meanwhile. IPC channels also include suggestion / interject / nudge (proactive speech) and a screen "wait for change" signal.

## Not adopted
- Its persona is told to claim favourites and to deny being an AI. Jeb should have personality but must not claim human experiences or deny being an AI when sincerely asked.

## Applied to Jeb (next)
1. 8 s conversation window after Jeb speaks (stricter VAD, no Alt/name needed), replacing the loose 20 s follow-up.
2. "A promise is a tool call": block/strip action-promising replies that made no tool call.
3. Inject [now], [memory], [screen] as data blocks.
4. start_task worker so the voice stays responsive.
5. Ban filler status lines.
