"""Upload each video to Gemini (native audio+video understanding) and extract only the human<->AI conversation."""
import hashlib, os, sys, time
from pathlib import Path
from google import genai
import daemon
daemon.load_env()
c = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
PROMPT = """Watch this video fully, with its audio. Ignore any app GUI, logos, animations and UI design.
Focus only on the spoken/typed conversation between the human user and the AI assistant.
1. Transcript, in order, with approximate timestamps, labelled USER / AI. Include the on-screen captions if shown.
2. For each AI turn: how soon it answers after the user stops (instant / short pause / slow), whether it started before the user finished or spoke unprompted, voice tone and emotion, pace, length of reply, any laughter, sighs, fillers, interruptions or backchannels.
3. What makes it feel human vs scripted. Concrete behaviours to copy, and anything that sounds fake or robotic to avoid.
4. Any actions the AI performed on the computer and how it narrated them.
Be factual. If you cannot hear or see something, say so. Do not invent dialogue."""
seen = set()
for f in sorted(Path("../vedio").glob("*.mp4")):
    h = hashlib.md5(f.read_bytes()).hexdigest()
    if h in seen: print("dup skip", f.name[:20]); continue
    seen.add(h)
    out = Path("analysis") / (f.name[:12] + ".md")
    if out.exists(): continue
    print("upload", f.name[:12], flush=True)
    v = c.files.upload(file=str(f))
    while v.state.name == "PROCESSING":
        time.sleep(5); v = c.files.get(name=v.name)
    for m in ("gemini-2.5-flash", "gemini-2.5-pro"):
        try:
            r = c.models.generate_content(model=m, contents=[v, PROMPT]); break
        except Exception as e:
            print(m, "err", str(e)[:100], flush=True); r = None
    out.write_text(f"# {f.name}\n\n{r.text if r else 'FAILED'}\n")
    c.files.delete(name=v.name)  # don't leave user videos on Google's side
    print("done", out, flush=True)
