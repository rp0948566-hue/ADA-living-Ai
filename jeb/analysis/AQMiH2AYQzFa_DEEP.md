# Deep analysis: "Jarvis hat Zugriff auf den gesamten Luftraum"

File: AQMiH2AYQzFa….mp4 (copy in `vedio/` is byte-identical). 58.6 s, 720x1280 vertical, 30 fps h264, AAC 44.1 kHz stereo.
Method: 59 frames at 1 fps with timestamps (all viewed), full-res crops of the data panels, faster-whisper `small` (German, word timestamps), per-second loudness. Earlier Gemini report (`AQMiH2AYQzFa.md`) used only as a cross-check; its timings are off by 1-3 s in places and it missed several things below.
Limit: I cannot hear. Voice character comes from whisper clarity, word timing and loudness only. "Deep male synthetic voice" is the earlier Gemini claim, not verified here.

## 1. What the video is
A phone filming a curved ASUS monitor on a desk. No person speaks. One-sided monologue by an AI called Jarvis, addressing the owner as "Master". TikTok-style caption (white rounded box) "Jarvis hat Zugriff auf den gesamten Luftraum" shown only 0-9 s, then removed. Dubai skyline (Burj Khalifa) is the wallpaper; the Jarvis UI floats over it. A small pill at top-centre of the screen shows a cursor icon plus level bars that animate while Jarvis speaks (listening/speaking indicator).
Setup revealed at 29-32 s when the camera pulls back: silver laptop at left, Logitech MX Keys (Mac, German layout) in front, a second screen with text at right edge.

## 2. Speech, word-timed (whisper, German; my corrections in brackets)
| t (s) | text |
|---|---|
| 1.80 | Master, |
| 3.96-7.6 | 11.631 Flugobjekte sind im Moment [in der Luft; screen counter says "Flugobjekte gerade in der Luft"] |
| 8.98-10.5 | Da ist eine Drohne. |
| 11.68-19.5 | MQ-9 Reaper. Britisch, laut Kennung. Aufklärungsdrohne. Kein Pilot an Bord. Ich habe sie heute geortet. |
| 20.02-27.5 | Südlich von Zypern, 5.100 Meter hoch, 280 Kilometer pro Stunde, Rufzeichen Cody 13. |
| 28.16-31.9 | Sie sendet offen. Jeder könnte zusehen. Nur schaut keiner hin. |
| 34.66-36 | Warten Sie mal. |
| 36.42-41.4 | Das hier ist kein normales Flugzeug: ein Beluga XL. Ein fliegender Wal. |
| 41.98-45.3 | In seinen Bauch passen zwei komplette Flügel eines Airbus. |
| 45.80-50 | Südwestlich von Belgien, 10.100 Meter hoch. |
| 50.54-52.5 | Er bringt Bauteile von Werk zu Werk. |
| 52.88-55 | Ich habe alles im Blick, Master. |

Whisper errors fixed: "geordnet"=geortet, "König zu sehen"=könnte zusehen, "Wahl"=Wal.
Rhythm: about 83 words in 53 s, roughly 95 words/min: slow, deliberate. Pauses: 1.5 s after "Drohne" (photo opens), 2.9 s after "hin" (zoom-out transition, covers "Warten Sie mal"), 1.2 s before "Er bringt", 1.0 s before the sign-off. Speech starts 0.8 s after the visuals start, so the UI leads and the voice follows.

## 3. Audio
Loudness is nearly flat: per-second mean -18.5 to -24.7 dBFS across the whole clip, including the gaps (-23 to -25 dB at 32-34 s). So there is a continuous bed (music/hum) under the voice, and the voice is heavily compressed (about 5 dB between speech and gaps). Opening: whirring charge-up sound over the white bloom at 1 s. Pitch tracking failed (autocorrelation locks onto the bed), so no f0 numbers. No laughs, breaths, fillers ("äh"), self-corrections or interruptions. Not one filler word in 53 s: it reads as scripted/pre-written lines read by TTS, not live LLM output.

## 4. Screen, frame by frame
- 0 s: wallpaper only (Dubai, night, haze).
- 1 s: white-to-orange glowing orb blooms in the centre (wake/boot pulse).
- 2 s: orb resolves into a wireframe-textured globe (Americas) with a red-orange atmospheric rim.
- 3 s: globe rotates to Asia; thin orbital ring with tick marks appears; label top-left "JARVIS · ORBITAL · LUFTBILD"; counter bottom-centre 2.048.
- 4-5 s: Africa/Europe in view, yellow-orange flight arcs and thousands of dots fill in; counter 11.180 then 11.631 (voice says the number at 4.0-4.4 s, so speech is synced to the counter).
- 6-9 s: camera dives toward Africa/Middle East, then Cyprus; red circle with white X and corner brackets locks onto one aircraft; range rings, coordinates strip at the bottom.
- 10-11 s: photo gallery panel appears left (large photo plus 4 thumbnails), data panel appears right.
- 12-17 s: gallery cycles about every 1.5 s: Reaper head-on on tarmac with a Humvee (12-14 s), Reaper at dusk/night (15-16 s, again 25-27 s), ground crew (28-29 s), Reaper in flight (31 s). Lower card: "FLUGOBJEKT · DROHNE · LIVE / MQ-9 Reaper / Aufklärungsdrohne" with a top-down silhouette and wingspan/length dimension lines.
- 18-23 s: transponder panel, legible at full resolution (21 s): Rufzeichen CODY13; Geortet südlich von Zypern; Herkunft britisch (laut Kennung); Kennzeichen PR-something; Höhe about 5.xxx m; Tempo 279 km/h; Steigrate 0,0 m/s; Kurs 235°; Squawk 7501 (digits blurry); Position 34.289° · 33.091°. Section "TECHNIK · HERSTELLER": Typ MQ-9 Reaper; Rolle Aufklärungsdrohne; Pilot keiner an Bord, gesteuert aus einer Bodenstation; Antrieb 1x Honeywell TPE331 Turboprop; Länge 11,0 m; Spannweite 20,1 m; In der Luft über 24 Stunden. Voice reads location, altitude, speed, call sign straight from these rows.
- 29-32 s: camera pulls back, UI unchanged; at 32 s the drone view dissolves into an unlabeled dense map with the target marked by brackets and a red dot.
- 33-34 s: zoom out to a globe of Europe with a dense mesh of yellow lines, then flat map with thick extruded yellow air-corridor ribbons.
- 35-41 s: target switches to an orange filled circle (civil/selected) with crosshair; gallery shows Beluga XL (belly gear and fuselage, take-off with the whale-face nose at 40 s, exactly when the voice says "fliegender Wal"). Lower card "Airbus Transport · BGA232R".
- 42-47 s: transponder panel (43 s): Rufzeichen BGA232R; Kennzeichen F-GXLO; Höhe about 10.0xx m; Tempo 686 km/h; Mach 0,668; Steigrate -0,3 m/s; Außentemp -42 °C; Wind 48 km/h aus 219°; Kurs 230°; Squawk 1361; Position 49.357° · 2.791° (northern France, consistent with "südwestlich von Belgien"). Technik: Airbus BelugaXL; 2x Rolls-Royce Trent 700; Länge 63,1 m; Spannweite 60,3 m; Nutzlast rund 51 Tonnen, zwei A350-Flügel; Reichweite rund 4.000 km.
- 48-55 s: map pans slowly with the corridors; panels removed; Jarvis says the sign-off.
- 56-58 s: zoom back out to the globe (Europe-centred), globe shrinks into an orange orb, orb fades, wallpaper only. Mirrors the 0-2 s opening.
Camera: handheld, close on the monitor 0-29 s, pull-back 29-33 s, push-in again, small hand shake throughout, no cuts. Everything is one continuous take.

## 5. Why it feels alive (copy) and what feels fake
Copy: the UI leads the voice and the voice only reads what is on screen (no invented facts); the number is spoken while the counter ticks; the photo changes on the key word; one dry observation ("Nur schaut keiner hin"), one playful image ("fliegender Wal"), one attention shift ("Warten Sie mal") make it sound like discovery; closing line restates role; short sentences, concrete numbers, no filler or "Sure!".
Fake or risky: no user turn, so it is a staged demo not a conversation; zero fillers/breaths; flat loudness; "heute geortet" is a claim of memory that the screen does not show; speed rounded (279 spoken as 280) and altitude spoken 5.100 while the panel's digits are not legible, so exactness cannot be confirmed; all data looks like live ADS-B but the video alone does not prove it is live.

## 6. For Jeb
- Narrate only what a tool returned (matches Jeb's honesty rule).
- Visual first, voice 0.5-1 s later; speak numbers while they appear.
- Long pause (1-3 s) allowed while the UI transitions; do not fill it.
- Gate: Jeb has no equivalent of the speaking-indicator pill; GUI could add one (events `state`).
