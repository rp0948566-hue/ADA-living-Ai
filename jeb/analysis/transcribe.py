import glob, os
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
seen = set()
for f in sorted(glob.glob("../../vedio/*.mp4")):
    k = os.path.getsize(f)
    if k in seen: continue
    seen.add(k)
    segs, info = m.transcribe(f, beam_size=1)
    with open("whisper_" + os.path.basename(f)[:12] + ".txt", "w") as o:
        o.write(f"lang={info.language}\n")
        for s in segs: o.write(f"[{s.start:5.1f}-{s.end:5.1f}] {s.text.strip()}\n")
    print("done", f[-20:], flush=True)
