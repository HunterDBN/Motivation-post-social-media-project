"""Schedule a day's rendered carousels on Instagram, Facebook and TikTok through Buffer's API.

Needs BUFFER_API_KEY in the environment (from publish.buffer.com/settings/api, saved as an
environment secret, never committed). Buffer fetches images from public URLs, so slides are
served from `media_base_url` in config.json (the repo's raw GitHub URL; the repo must be public
and the day's output pushed before running --live).

Usage:
  python -m buddha_post.publish --list-channels          # find channel ids for config.json
  python -m buddha_post.publish 2026-11-14 [--live] [--post N]
Dry run unless --live. Writes output/DATE/published.json.
"""
import json, os, sys, urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT/"config.json").read_text())
API = "https://api.buffer.com"

def gql(query, variables=None):
    key = os.environ.get("BUFFER_API_KEY") or sys.exit("BUFFER_API_KEY is not set")
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    res = json.loads(urllib.request.urlopen(req, timeout=60).read())
    if res.get("errors"): sys.exit(f"Buffer error: {res['errors']}")
    return res["data"]

def list_channels():
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    for o in orgs:
        chans = gql("query($id: OrganizationId!) { channels(input: {organizationId: $id}) { id name service } }",
                    {"id": o["id"]})["channels"]
        for c in chans: print(f'{c["service"]:10} {c["id"]}  {c["name"]}  (org {o["name"]})')

CREATE = """mutation($input: CreatePostInput!) { createPost(input: $input) {
  ... on PostActionSuccess { post { id dueAt } } ... on MutationError { message } } }"""

def main(day, live=False, only=None):
    tz = ZoneInfo(CFG["timezone"]); channels = CFG["buffer_channels"]; results = {}
    base = CFG["media_base_url"].rstrip("/")
    for d in sorted((ROOT/"output"/day).glob("post-*")):
        n = int(d.name.split("-")[1])
        if only and n != only: continue
        meta = json.loads((d/"meta.json").read_text())
        hh, mm = map(int, meta["time"].split(":"))
        when = datetime.fromisoformat(day).replace(hour=hh, minute=mm, tzinfo=tz)
        urls = [f"{base}/{day}/{d.name}/{s.name}" for s in sorted(d.glob("slide-*.jpg"))]
        text = (d/"caption.txt").read_text()
        if not live:
            print(f"[dry run] {d.name} at {when:%Y-%m-%d %H:%M %Z}: {len(urls)} slides -> {list(channels)}")
            continue
        if when < datetime.now(tz): sys.exit(f"{d.name}: {when} is already in the past")
        for platform, cid in channels.items():
            if not cid: continue
            inp = {"channelId": cid, "text": text, "schedulingType": "automatic", "mode": "customScheduled",
                   "dueAt": when.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z"),
                   "assets": [{"image": {"url": u}} for u in urls]}
            if platform == "facebook": inp["metadata"] = {"facebook": {"type": "post"}}
            r = gql(CREATE, {"input": inp})["createPost"]
            results[f"{d.name}/{platform}"] = r; print(d.name, platform, r)
    if live: (ROOT/"output"/day/"published.json").write_text(json.dumps(results, indent=1))

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--list-channels" in a: list_channels()
    else: main(a[0], "--live" in a, int(a[a.index("--post")+1]) if "--post" in a else None)
