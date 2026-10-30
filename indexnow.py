"""Tell Bing (and other IndexNow engines) about new or updated pages right after a deploy."""
import datetime as dt, json, re, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
key_file = next((ROOT / "static").glob("indexnow-*.txt"))
KEY = key_file.read_text().strip()
sm = (ROOT / "public/sitemap.xml").read_text()
base = re.search(r"<loc>(https://[^/]+)", sm).group(1)
host = base.split("//")[1]
cut = dt.date.today() - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 2)
urls = []
for loc, mod in re.findall(r"<loc>([^<]+)</loc>(?:<lastmod>([^<]+)</lastmod>)?", sm):
    if loc.rstrip("/") == base or (mod and dt.date.fromisoformat(mod) >= cut):
        urls.append(loc)
body = json.dumps({"host": host, "key": KEY, "keyLocation": f"{base}/{key_file.name}", "urlList": urls}).encode()
for attempt in range(6):  # Hostinger pulls the deploy branch shortly after the push
    try:
        req = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
        r = urllib.request.urlopen(req, timeout=30)
        print("IndexNow", r.status, len(urls), "urls:", *urls, sep="\n  ")
        break
    except Exception as e:
        print("IndexNow attempt", attempt + 1, "failed:", e)
        time.sleep(60)
