"""List what Buffer really has per day (Vancouver AND Da Nang time) and flag shortfalls.
Expected per day: 6 feed posts on every channel + 10 stories on Instagram.
Buffer's free plan only holds 10 scheduled items per channel, so far-ahead slots can't be queued yet.
The hard check is therefore: every rendered slot due in the next 8 hours must be in Buffer (otherwise FAIL).
Per-day counts in Vancouver and Da Nang time are printed for information; "(topup fills later)" = plan limit.
Usage: python -m buddha_post.verify [YYYY-MM-DD ...]   (default: today, tomorrow, day after)"""
import json, os, sys, urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
CFG = json.loads((Path(__file__).resolve().parent.parent/"config.json").read_text())
TZ = ZoneInfo(CFG["timezone"]); FEED = CFG.get("posts_per_day", 6); STORIES = CFG["stories"]["per_day"]
def gql(q, v=None):
    r = urllib.request.Request("https://api.buffer.com", data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["BUFFER_API_KEY"], "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())
def main(days, tz, must):
    org = gql("{account{organizations{id}}}")["data"]["account"]["organizations"][0]["id"]
    lo = (datetime.fromisoformat(min(days)).replace(tzinfo=tz) - timedelta(days=1)).astimezone(ZoneInfo("UTC")); hi = (datetime.fromisoformat(max(days)).replace(tzinfo=tz) + timedelta(days=2)).astimezone(ZoneInfo("UTC"))
    f = "%Y-%m-%dT%H:%M:%SZ"; res = []; after = None
    while True:
        r = gql('query($o:OrganizationId!,$s:DateTime,$e:DateTime,$a:String){posts(first:100,after:$a,input:{organizationId:$o,filter:{dueAt:{start:$s,end:$e}}}){pageInfo{hasNextPage endCursor} edges{node{status dueAt channelService metadata{... on InstagramPostMetadata{type}}}}}}',
                {"o": org, "s": lo.strftime(f), "e": hi.strftime(f), "a": after})["data"]["posts"]
        res += r["edges"]
        if not r["pageInfo"]["hasNextPage"]: break
        after = r["pageInfo"]["endCursor"]
    ok = True
    for d in days:
        feed, st = Counter(), Counter()
        for e in res:
            n = e["node"]; t = datetime.fromisoformat(n["dueAt"].replace("Z", "+00:00")).astimezone(tz)
            if t.strftime("%Y-%m-%d") != d or n["status"] not in ("scheduled", "sending", "sent"): continue
            if (n.get("metadata") or {}).get("type") == "story": st[n["channelService"]] += 1
            else: feed[n["channelService"]] += 1
        for ch in [k for k, v in CFG["buffer_channels"].items() if v]:
            want = [("feed", feed[ch], FEED)] + ([("stories", st[ch], STORIES)] if ch == CFG["stories"]["channel"] else [])
            line = " ".join(f"{k}={c}/{w}" for k, c, w in want)
            short = any(c < w for _, c, w in want); gate = d in must
            print(f"{d} ({tz.key}) {ch}: {line}" + ("  (topup fills later: plan queue limit)" if short else "  OK"))
    return True

def horizon_ok(hours=8):
    from buddha_post import topup
    now = datetime.now(TZ); days = [(now + timedelta(days=i)).strftime("%Y-%m-%d") for i in (0, 1)]
    have = topup.P.existing(days[0]); bad = []
    for when, cid, plat, name, day, _ in topup.slots(days):
        due = when.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
        if now < when < now + timedelta(hours=hours) and (cid, due) not in have: bad.append(f"{day} {name} {plat} {when:%H:%M}")
    print("next-8h check:", "all slots queued" if not bad else "MISSING " + ", ".join(bad))
    return not bad
if __name__ == "__main__":
    today = datetime.now(TZ)
    days = sys.argv[1:] or [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in (0, 1, 2)]
    must = set()
    # today's slots already published count as sent; Hunter views Buffer in Da Nang time, so check both timezones
    a = main(days, ZoneInfo(CFG["view_timezone"]), must); b = main(days, TZ, must)
    sys.exit(0 if (a and b and horizon_ok()) else 1)
