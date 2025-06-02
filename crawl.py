"""
crawl.py – sammelt aktuelle KI-Business-Artikel
Speichert Ergebnis als articles.json
"""

import feedparser
import requests, json, re, hashlib
from datetime import datetime, timedelta, timezone
from dateutil import parser as dtparse
from pathlib import Path
from tqdm import tqdm

# -------- Quellen (RSS + JSON API) ------------------------------------------
RSS_FEEDS = [
    # Venture / Tech-Business
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://www.ben-evans.com/benedictevans?format=rss",
    # KI-Start-ups, Funding, M&A
    "https://www.ai-startups.org/feed",
    # deutschsprachige
    "https://www.handelsblatt.com/contentexport/feeds/TechAI",
]

NEWSAPI_KEY = ""   # optional – wenn du einen NewsAPI-Key hast

# Schlüsselbegriffe, die „geschäftsrelevante“ Meldungen markieren
KEYWORDS = [
    "business model", "commercial", "revenue", "subscription",
    "startup", "funding", "investment", "series", "seed",
    "licensing", "partnership", "enterprise",
    "Geschäftsmodell", "Finanzierungsrunde", "Umsatz",
]

MAX_AGE_H = 24       # nur Artikel der letzten 24 h
MAX_ARTICLES = 30    # hartes Limit pro Tag

# ---------------------------------------------------------------------------
def kw_score(txt: str) -> int:
    txt_l = txt.lower()
    return sum(1 for k in KEYWORDS if k in txt_l)

def normalize_url(url: str) -> str:
    return url.split("?")[0].strip("/")

def fetch_rss() -> list[dict]:
    articles = []
    now = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_H)
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if not getattr(entry, "link", None):
                continue
            pub = dtparse.parse(getattr(entry, "published", datetime.utcnow().isoformat()))
            if pub < now:
                continue
            title = entry.title
            desc  = getattr(entry, "summary", "")
            score = kw_score(title + " " + desc)
            if score == 0:
                continue
            articles.append(
                dict(
                    id=hashlib.sha1(entry.link.encode()).hexdigest()[:10],
                    title=title,
                    summary=re.sub("<[^>]+>", "", desc)[:400],
                    url=normalize_url(entry.link),
                    published=pub.isoformat(),
                    score=score,
                    source=url,
                )
            )
    # sortiert nach Keyword-Score und Aktualität
    articles.sort(key=lambda a: (-a["score"], a["published"]), reverse=False)
    return articles[:MAX_ARTICLES]

def main() -> None:
    arts = fetch_rss()
    Path("articles.json").write_text(json.dumps(arts, indent=2, ensure_ascii=False))
    print(f"✅  {len(arts)} Artikel gespeichert → articles.json")

if __name__ == "__main__":
    main()
