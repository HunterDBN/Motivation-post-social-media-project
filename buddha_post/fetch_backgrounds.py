"""Download CC0 / public-domain background photos via the Openverse API into backgrounds/,
recording source + license for each in backgrounds/credits.json."""
import json, time, urllib.request, urllib.parse, sys
from pathlib import Path
OUT = Path(__file__).parent.parent/"backgrounds"; OUT.mkdir(exist_ok=True)
CRED = OUT/"credits.json"
credits = json.loads(CRED.read_text()) if CRED.exists() else {}
QUERIES = sys.argv[1:] or ["grass lawn","park path","outdoor stairs","sunset field","lake",
    "forest trail","meadow sky","garden","clouds blue sky","beach shore","mountain view","park bench"]
PER = 5
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "quote-bg-fetcher/1.0"})
    return urllib.request.urlopen(req, timeout=40).read()
for q in QUERIES:
    qs = urllib.parse.urlencode({"q": q, "license": "cc0,pdm", "category": "photograph",
                                 "size": "large", "page_size": 20})
    try: res = json.loads(get(f"https://api.openverse.org/v1/images/?{qs}"))["results"]
    except Exception as e: print("search failed", q, e); time.sleep(5); continue
    n = 0
    for r in res:
        if n >= PER: break
        if r["id"] in credits or (r.get("width") or 0) < 1500: continue
        try: data = get(f"https://api.openverse.org/v1/images/{r['id']}/thumb/?full_size=true&compressed=false")
        except Exception as e: print("  dl failed", r["id"], e); continue
        if len(data) < 30000: continue
        fn = f"{q.replace(' ','_')}_{r['id'][:8]}.jpg"; (OUT/fn).write_bytes(data)
        credits[r["id"]] = {"file": fn, "query": q, "license": r["license"], "source": r.get("source"),
                            "landing": r.get("foreign_landing_url"), "creator": r.get("creator")}
        n += 1; time.sleep(0.5)
    print(q, n); time.sleep(2)
CRED.write_text(json.dumps(credits, indent=1))
print("total", len(credits))
