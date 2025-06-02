"""
crawl.py  –  sammelt tagesaktuelle KI-Business-Meldungen
Speichert Ergebnis als articles.json
"""

import feedparser, json, re, hashlib, requests
from datetime import datetime, timedelta, timezone
from dateutil import parser as dp
from pathlib import Path

RSS = [
    # International
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed",
    "https://www.ben-evans.com/benedictevans?format=rss",
    "https://aiinvestor.substack.com/feed",
    # Funding & Deals
    "https://ai-startups.org/feed",
    "https://feeds.feedburner.com/crunchbase-news",
    # DACH
    "https://www.handelsblatt.com/contentexport/feeds/TechAI",
    "https://t3n.de/rss.xml",
    # Heise AI-Ticker JSON
    "https://www.heise.de/hct/fakten/471/api/news/ai",
]

KEYWORDS = [
    "business model", "commercial", "revenue", "subscription",
    "startup", "funding", "series", "seed", "investment",
    "licensing", "partnership", "enterprise",
    "Geschäftsmodell", "Finanzierungsrunde", "Umsatz",
]

MAX_H = 36     # bis zu 36 Stunden zurück
MAX_N = 40     # Obergrenze Artikel

def kscore(txt: str) -> int:
    t = txt.lower()
    return sum(k in t for k in KEYWORDS)

def add_article(store, title, url, summary, pub, src):
    if kscore(title + summary) == 0:
        return
    store.append(
        dict(
            id=hashlib.md5(url.encode()).hexdigest()[:10],
            title=title.strip(),
            summary=re.sub("<[^>]+>", "", summary)[:400],
            url=url,
            published=pub.isoformat(),
            source=src,
        )
    )

def fetch_rss():
    arts, now = [], datetime.now(timezone.utc) - timedelta(hours=MAX_H)
    for src in RSS[:-1]:  # alle außer Heise-API
        feed = feedparser.parse(src)
        for e in feed.entries:
            if not getattr(e, "link", None):
                continue
            pub = dp.parse(getattr(e, "published", datetime.utcnow().isoformat()))
            if pub < now:
                continue
            add_article(arts, e.title, e.link, getattr(e, "summary", ""), pub, src)
    return arts

def fetch_heise(store):
    try:
        data = requests.get(RSS[-1], timeout=10).json()
        for n in data["data"][:10]:
            pub = dp.parse(n["date"])
            add_article(store, n["title"], n["url"], n["teaser"], pub, "heise.ai")
    except Exception:
        pass

def main():
    articles = fetch_rss()
    fetch_heise(articles)
    # Score & Limit
    articles.sort(key=lambda a: (-kscore(a["title"]), a["published"]))
    Path("articles.json").write_text(json.dumps(articles[:MAX_N], ensure_ascii=False, indent=2))
    print(f"✅  {len(articles[:MAX_N])} Artikel gespeichert → articles.json")

if __name__ == "__main__":
    main()
