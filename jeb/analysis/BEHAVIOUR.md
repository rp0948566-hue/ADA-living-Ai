# What the videos show (6 videos, Gemini watched audio+video; frames checked on 2 of them)
1. Airspace "Jarvis": speaks first, unprompted, narrating live data. Dry observation after facts ("it broadcasts openly... nobody looks"), a transition cue ("hold on"), one vivid image ("a flying whale"), calm confident close.
2. "Two brains" AI: one fast voice that keeps talking while a separate planner does the work in the background. Replies to thanks after ~0.5-1 s, by name, referencing context.
3. Local-brain Jarvis: starts answering as the user finishes. Humour from the data itself (the calendar slot named "Busy"), self-aware jokes about itself. Says what it is about to do before acting ("let me see if I have the tools for that"), then reports results with an opinion. Frames show a status line "reaching for the tools" during the action.
4. Voice-command Jarvis: ultra-short confirmations ("Searching." "Closed." "Launching."). Notices state: Steam already running -> brings it forward instead of relaunching.
5. Mac co-founder agent: friendly greeting, explains and then offers the next step ("Want to learn more?"), ties explanation to something the user can do.
6. EXCLUDED: money-app pitch (wrong video, no AI; user confirmed).

# Weak points the analyses flagged (avoid)
- Same rhythm and tone every turn. Formulaic "..., sir" endings. No variation in phrasing. Always instant replies, never a beat.

# Rules adopted for Jeb
- Voice loop never blocks: answer/narrate immediately, run actions in a worker, report when done.
- Before an action: one short line. After: result plus one real observation if there is one.
- Check state before acting; say when it is already done.
- Vary confirmations; confirmations 1-3 words. Occasional short beat before replying to emotional or thinking questions.
- Speak unprompted only with a concrete finding. Humour comes from the facts at hand.
- No "sir"/"Master".

# Frame-by-frame findings (every video, 1 frame / 2 s, all sheets viewed)
- v1 airspace: visuals track the speech. Counter climbs 329 -> 11,630 -> 11,631 while it says the number; a red lock-on marker appears when it says "there's a drone"; photo + data panel appear as it describes the aircraft; map zooms to the next region on "hold on". Narration and screen state change together.
- v2 two brains: word-by-word kinetic captions; ambient room lighting changes colour with the story; the AI is an orb on screen, the person only reacts.
- v3 local brain: ring HUD shows SPEAKING + active model chip; a status line "reaching for the tools" shows while it acts; calendar events get numbered markers exactly as it says "three items"; a text transcript of its reply sits under the HUD; ends with a comment-for-resources call to action.
- v4 voice commands: liquid-orb animation reacts to voice; actions complete within ~1 s of the command (browser, search results, Steam foreground, launch pop-up).
- v5 Vovy: avatar flies to the dock icon before acting; push-to-talk hotkey (fn+control); circle-to-ask (option+control) opens a small explanation card with the code highlighted; avatar has selectable characters.
- v6: excluded (wrong video).
=> For Jeb: the "feel" comes from sync (speech and on-screen state move together), a visible status for what it is doing, and instant tiny confirmations. Whisper audio cross-check of Gemini's transcripts is still pending (small model still downloading).

# Techniques taken from the 5 AI videos (each from a different one)
1 airspace: speak first with a concrete finding + one dry observation; sync speech with what is happening.
2 two-brains: voice never blocks; replies to thanks with a short beat, by name, referencing earlier context.
3 local-brain: narrate before acting; humour from the facts; self-aware jokes; show what it is doing.
4 voice-commands: 1-3 word confirmations, sub-second; check state first (already running -> bring forward).
5 Vovy: casual intro, offer a next step only when it is genuinely useful; hotkey or circle-to-ask to give screen context.
Flaws they all share (fixed in Jeb): uniform rhythm, repeated "sir", identical confirmations, no rare filler, always-instant timing.
