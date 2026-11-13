"""Render a day's carousels from content/YYYY-MM-DD.json.

content file format:
{"posts": [{"theme": "...", "quotes": ["slide 1", "slide 2", "slide 3", "slide 4"], "caption": "..."}]}

Picks backgrounds not used in the last 10 days, renders output/DATE/post-N/slide-K.jpg + caption.txt,
and appends every quote and background to history.json so they don't repeat.
Usage: python -m buddha_post.build_day 2026-11-14
"""
import json, random, sys
from pathlib import Path
from datetime import date, timedelta
from buddha_post.make_slide import make

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT/"config.json").read_text())
HIST = ROOT/"history.json"

def norm(q): return " ".join(q.lower().split())

def main(day):
    spec = json.loads((ROOT/"content"/f"{day}.json").read_text())
    hist = json.loads(HIST.read_text()) if HIST.exists() else {"quotes": {}, "backgrounds": {}}
    used_q = set(hist["quotes"])
    cutoff = (date.fromisoformat(day) - timedelta(days=10)).isoformat()
    recent_bg = {b for b, d in hist["backgrounds"].items() if d >= cutoff}
    bgs = sorted(p.name for p in (ROOT/"backgrounds").glob("*.jpg"))
    pool = [b for b in bgs if b not in recent_bg] or bgs
    random.seed(day); random.shuffle(pool)
    dupes = [q for p in spec["posts"] for q in p["quotes"] if norm(q) in used_q]
    if dupes: sys.exit(f"Already-posted quotes, rewrite them: {dupes}")
    out_day = ROOT/"output"/day
    for i, post in enumerate(spec["posts"], 1):
        d = out_day/f"post-{i}"; d.mkdir(parents=True, exist_ok=True)
        side = "left" if i % 2 else "right"
        for k, q in enumerate(post["quotes"], 1):
            bg = pool.pop() if pool else random.choice(bgs)
            make(ROOT/"backgrounds"/bg, q, d/f"slide-{k}.jpg", side)
            hist["quotes"][norm(q)] = day; hist["backgrounds"][bg] = day
        tags = " ".join(CFG["hashtags"])
        (d/"caption.txt").write_text(post["caption"].strip() + "\n\n" + tags + "\n")
        (d/"meta.json").write_text(json.dumps({"theme": post.get("theme"), "time": CFG["post_times"][i-1] if i <= len(CFG["post_times"]) else None}))
        print("rendered", d)
    HIST.write_text(json.dumps(hist, indent=1))

if __name__ == "__main__":
    main(sys.argv[1])
