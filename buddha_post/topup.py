"""Fill Buffer's queue, earliest slot first, until the plan's limit says stop.

Buffer's free plan keeps only 10 scheduled items per channel at once (feed posts AND stories count).
Instagram needs 16 items/day (6 posts + 10 stories), so the run happens every ~6 hours and each run
schedules the next slots that fit. Safe to re-run: slots already in Buffer are skipped.
Usage: python -m buddha_post.topup [--live] [YYYY-MM-DD ...]   (default: today..tomorrow, Vancouver)"""
import json, sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from buddha_post import publish as P

ROOT, CFG = P.ROOT, P.CFG
TZ = ZoneInfo(CFG["timezone"]); UTC = ZoneInfo("UTC"); F = "%Y-%m-%dT%H:%M:%SZ"

def slots(days):
    """[(due_utc, channel, platform, kind, day, name)] for every rendered slot."""
    out = []; base = CFG["media_base_url"].rstrip("/")
    for day in days:
        for d in sorted((ROOT/"output"/day).glob("post-*")):
            meta = json.loads((d/"meta.json").read_text()); hh, mm = map(int, meta["time"].split(":"))
            when = datetime.fromisoformat(day).replace(hour=hh, minute=mm, tzinfo=TZ)
            urls = [f"{base}/{day}/{d.name}/{s.name}" for s in sorted(d.glob("slide-*.jpg"))]
            text = (d/"caption.txt").read_text()
            for plat, cid in CFG["buffer_channels"].items():
                if not cid: continue
                inp = {"channelId": cid, "text": text, "assets": [{"image": {"url": u}} for u in urls]}
                if plat == "tiktok": inp["metadata"] = {"tiktok": {"title": text.split("\n")[0][:90], "isAiGenerated": False}}
                if plat == "instagram": inp["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
                if plat == "facebook": inp["metadata"] = {"facebook": {"type": "post"}}
                out.append((when, cid, plat, f"{d.name}", day, inp))
        sd = ROOT/"output"/day/"stories"
        if (sd/"meta.json").exists():
            cid = CFG["buffer_channels"][CFG["stories"]["channel"]]
            for n, t in enumerate(json.loads((sd/"meta.json").read_text())["times"], 1):
                hh, mm = map(int, t.split(":")); when = datetime.fromisoformat(day).replace(hour=hh, minute=mm, tzinfo=TZ)
                inp = {"channelId": cid, "text": "", "assets": [{"image": {"url": f"{base}/{day}/stories/story-{n}.jpg"}}],
                       "metadata": {"instagram": {"type": "story", "shouldShareToFeed": False}}}
                out.append((when, cid, CFG["stories"]["channel"], f"story-{n}", day, inp))
    return sorted(out, key=lambda x: x[0])

def main(days, live):
    have = P.existing(days[0]); now = datetime.now(TZ); full = set(); added = 0
    for when, cid, plat, name, day, inp in slots(days):
        due = when.astimezone(UTC).strftime(F)
        if when < now or (cid, due) in have or cid in full: continue
        inp.update({"schedulingType": "automatic", "mode": "customScheduled", "dueAt": due})
        if not live: print(f"[dry run] {day} {name} {plat} {when:%H:%M}"); continue
        r = P.gql(P.CREATE, {"input": inp})["createPost"]
        if "post" in r: added += 1; print(day, name, plat, f"{when:%H:%M}", "scheduled")
        else: full.add(cid); print(day, name, plat, f"{when:%H:%M}", "-> queue full:", r.get("message"))
    print(f"scheduled {added}; channels at their plan limit: {sorted(full) or 'none'}")

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    days = a or [(datetime.now(TZ)+timedelta(days=i)).strftime("%Y-%m-%d") for i in (0, 1)]
    main(days, "--live" in sys.argv)
