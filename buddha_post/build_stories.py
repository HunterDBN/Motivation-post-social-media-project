"""Render a day's 10 Instagram stories (1080x1920) from OLD content, so reuse is fine.

Pool = every quote ever used in feed posts (history.json) that is at least 3 days old
       + content/bank.json (verified real quotes and short modern lines not yet used anywhere).
Stories rotate through the whole pool before any quote repeats (story_history.json).
Mix per day: at most 3 from the same source, 5+ different sources where possible.
Usage: python -m buddha_post.build_stories YYYY-MM-DD
Writes output/DATE/stories/story-K.jpg and meta.json (times from config.json -> stories.times)."""
import json, random, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from buddha_post.make_story import make

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT/"config.json").read_text())
SH = ROOT/"story_history.json"
def norm(q): return " ".join(q.lower().split())
def src(q): return norm(q.partition("||")[2]) or "modern"

def pretty(q):
    """history.json stores lowercase; restore sentence case and a title-case attribution for display."""
    t, _, by = q.partition("||")
    t = t[:1].upper() + t[1:]
    for sep in (". ", "; "):
        if sep == ". ": t = ". ".join(x[:1].upper()+x[1:] for x in t.split(". "))
    return t + ("||" + by.title() if by else "")

def pool(day):
    hist = json.loads((ROOT/"history.json").read_text())
    cutoff = (date.fromisoformat(day) - timedelta(days=3)).isoformat()
    items = {}
    for q, d in hist["quotes"].items():
        if d <= cutoff: items[norm(q)] = pretty(q)
    # bank quotes are shown with their attribution
    bank = json.loads((ROOT/"content"/"bank.json").read_text())
    for r in bank["real"]: items.setdefault(norm(r["q"]+"||"+r["by"]), r["q"]+"||"+r["by"])
    for m in bank["modern"]: items.setdefault(norm(m), m)
    return items

def main(day):
    n = CFG["stories"]["per_day"]; times = CFG["stories"]["times"][:n]
    sh = json.loads(SH.read_text()) if SH.exists() else {}
    items = pool(day)
    fresh = [k for k in items if k not in sh]
    if len(fresh) < n:  # whole pool used once: start another lap with the oldest-used first
        fresh += sorted((k for k in items if k in sh), key=lambda k: sh[k])[: n*3]
    rng = random.Random("stories"+day); rng.shuffle(fresh)
    chosen, cnt = [], Counter()
    for k in fresh:  # variety: cap any one source at 3 a day
        s = src(items[k])
        if cnt[s] < 3: chosen.append(k); cnt[s] += 1
        if len(chosen) == n: break
    bgs = sorted(p.name for p in (ROOT/"backgrounds").glob("*.jpg")); rng.shuffle(bgs)
    out = ROOT/"output"/day/"stories"; out.mkdir(parents=True, exist_ok=True)
    for i, k in enumerate(chosen, 1):
        make(ROOT/"backgrounds"/bgs[i % len(bgs)], items[k], out/f"story-{i}.jpg", "left" if i % 2 else "right")
        sh[k] = day
    (out/"meta.json").write_text(json.dumps({"times": times[:len(chosen)], "sources": dict(cnt)}))
    SH.write_text(json.dumps(sh, indent=1)); print(f"rendered {len(chosen)} stories", dict(cnt), f"pool {len(items)}, unused left {len([k for k in items if k not in sh])}")

if __name__ == "__main__":
    main(sys.argv[1])
