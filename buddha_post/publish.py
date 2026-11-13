"""Schedule a day's rendered carousels on Instagram, Facebook and TikTok through Ayrshare.

Needs AYRSHARE_API_KEY in the environment (a saved environment secret, never committed).
Dry run by default; pass --live to actually schedule. Writes output/DATE/published.json.
Usage: python -m buddha_post.publish 2026-11-14 [--live] [--post N]
"""
import base64, json, os, sys, urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT/"config.json").read_text())
API = "https://api.ayrshare.com/api"

def call(path, body, key):
    req = urllib.request.Request(f"{API}/{path}", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=120).read())

def upload(img, key):
    b64 = base64.b64encode(img.read_bytes()).decode()
    return call("media/upload", {"file": f"data:image/jpeg;base64,{b64}", "fileName": img.name}, key)["url"]

def main(day, live=False, only=None):
    key = os.environ.get("AYRSHARE_API_KEY")
    if live and not key: sys.exit("AYRSHARE_API_KEY is not set")
    tz = ZoneInfo(CFG["timezone"]); results = {}
    for d in sorted((ROOT/"output"/day).glob("post-*")):
        n = int(d.name.split("-")[1])
        if only and n != only: continue
        meta = json.loads((d/"meta.json").read_text())
        hh, mm = map(int, meta["time"].split(":"))
        when = datetime.fromisoformat(day).replace(hour=hh, minute=mm, tzinfo=tz)
        slides = sorted(d.glob("slide-*.jpg"))
        body = {"post": (d/"caption.txt").read_text(), "platforms": CFG["platforms"],
                "scheduleDate": when.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tikTokOptions": {"autoAddMusic": True}}
        if not live:
            print(f"[dry run] {d.name} at {when:%Y-%m-%d %H:%M %Z}: {len(slides)} slides -> {body['platforms']}")
            continue
        if when < datetime.now(tz): sys.exit(f"{d.name}: {when} is already in the past")
        body["mediaUrls"] = [upload(s, key) for s in slides]
        results[d.name] = call("post", body, key)
        print(d.name, results[d.name].get("status"), results[d.name].get("id"))
    if live: (ROOT/"output"/day/"published.json").write_text(json.dumps(results, indent=1))

if __name__ == "__main__":
    a = sys.argv[1:]
    only = int(a[a.index("--post")+1]) if "--post" in a else None
    main(a[0], "--live" in a, only)
