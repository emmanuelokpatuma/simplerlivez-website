#!/usr/bin/env python3
"""Build simplerlivez.com into ./public. Each file in pages/ is a Jinja template
that extends base.html and sets title/description/path via {% set %}."""
import datetime as dt, re, shutil
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
OUT = ROOT / "public"
SITE = yaml.safe_load((ROOT / "site.yml").read_text())
env = Environment(loader=FileSystemLoader([ROOT / "templates", ROOT / "pages"]),
                  autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)


def links():
    u = SITE["utm"]
    add = lambda url: url + ("&" if "?" in url else "?") + u
    return {"play": add(SITE["app"]["play_url"]), "ios": add(SITE["app"]["ios_url"])}


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    ctx = {"site": SITE, "links": links(), "year": dt.date.today().year}
    urls = []
    for p in sorted((ROOT / "pages").glob("*.html")):
        path = "/" if p.stem == "index" else f"/{p.stem}/"
        html = env.get_template(p.name).render(**ctx, path=path)
        dest = OUT / ("index.html" if path == "/" else "404.html" if p.stem == "404" else f"{p.stem}/index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        if "noindex" not in html[:3000]:
            urls.append(path)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{SITE['url']}{u}</loc><lastmod>{dt.date.today()}</lastmod></url>" for u in urls]
    (OUT / "sitemap.xml").write_text("\n".join(sm + ["</urlset>"]))
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    if SITE.get("adsense_client"):
        (OUT / "ads.txt").write_text(f"google.com, {SITE['adsense_client'].replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n")
    print("built", len(urls), "pages:", ", ".join(urls))


if __name__ == "__main__":
    main()
