"""List what Buffer really has scheduled per day (Vancouver time) and flag days with fewer than 4 posts per channel.
Usage: python -m buddha_post.verify [YYYY-MM-DD ...]   (default: next 3 days)"""
import json, os, sys, urllib.request
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
CFG = json.loads((Path(__file__).resolve().parent.parent/"config.json").read_text())
TZ = ZoneInfo(CFG["timezone"])
def gql(q, v=None):
    r = urllib.request.Request("https://api.buffer.com", data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Authorization": "Bearer " + os.environ["BUFFER_API_KEY"], "Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(r, timeout=60).read())
def main(days, tz=None):
    tz = tz or TZ
    org = gql("{account{organizations{id}}}")["data"]["account"]["organizations"][0]["id"]
    lo = (datetime.fromisoformat(min(days)).replace(tzinfo=tz) - timedelta(days=1)).astimezone(ZoneInfo("UTC")); hi = (datetime.fromisoformat(max(days)).replace(tzinfo=tz) + timedelta(days=2)).astimezone(ZoneInfo("UTC"))
    f = "%Y-%m-%dT%H:%M:%SZ"
    res = gql('query($o:OrganizationId!,$s:DateTime,$e:DateTime){posts(first:100,input:{organizationId:$o,filter:{dueAt:{start:$s,end:$e}}}){edges{node{status dueAt channelService assets{mimeType}}}}}',
              {"o": org, "s": lo.strftime(f), "e": hi.strftime(f)})["data"]["posts"]["edges"]
    ok = True
    for d in days:
        c = Counter(); times = []
        for e in res:
            n = e["node"]; t = datetime.fromisoformat(n["dueAt"].replace("Z", "+00:00")).astimezone(tz)
            if t.strftime("%Y-%m-%d") == d and n["status"] in ("scheduled", "sending", "sent"):
                c[n["channelService"]] += 1; times.append(f'{t:%H:%M}/{len(n["assets"])}img')
        for ch in [k for k, v in CFG["buffer_channels"].items() if v]:
            flag = "" if c[ch] >= 4 else "  <-- FEWER THAN 4"; ok &= c[ch] >= 4
            print(f"{d} ({tz.key}) {ch}: {c[ch]} posts {sorted(times) if ch == 'facebook' else ''}{flag}")
    sys.exit(0 if ok else 1)
if __name__ == "__main__":
    days = sys.argv[1:] or [(datetime.now(TZ) + timedelta(days=i)).strftime("%Y-%m-%d") for i in (1, 2, 3)]
    # Hunter views Buffer in Da Nang time: every day on his calendar must show 4 as well as every Vancouver day
    try: main(days, ZoneInfo(CFG["view_timezone"]))
    except SystemExit as e: bad = e.code
    else: bad = 0
    try: main(days)
    except SystemExit as e: bad = bad or e.code
    sys.exit(bad)
