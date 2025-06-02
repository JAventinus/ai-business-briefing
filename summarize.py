"""
summarize.py – erstellt Podcast-Skript aus articles.json
• Wenn keine Artikel: kurzer Hinweis-Text statt Fehler
"""

import json, os, sys, openai, datetime
from pathlib import Path

MODEL = "gpt-4o-mini"
TOKENS = 2_800
TEMP = 0.4

TEMPLATE = """\
Du bist Redakteur eines deutschsprachigen Podcasts über KI-Geschäftsmodelle.
Nutze die Quellen, um eine 15–20-min Episode (~2 000 Wörter) zu schreiben:

# Headline
## Intro
### Top-Stories
### Deep-Dive
### Take-aways
### Call-to-Action
"""

FALLBACK_TEXT = """\
# AI Business Briefing
## Intro
Heute gibt es keine relevanten neuen Meldungen zu KI-Geschäftsmodellen. \
Wir melden uns morgen wieder mit frischen Nachrichten.
"""

def load():
    if not Path("articles.json").is_file():
        return []
    return json.loads(Path("articles.json").read_text())

def main():
    arts = load()
    if not arts:
        Path("script.txt").write_text(FALLBACK_TEXT)
        print("ℹ️  Keine Artikel – Fallback-Text geschrieben.")
        return

    bullets = "\n".join(f"- {a['title']} ({a['url']})" for a in arts[:12])
    prompt = TEMPLATE + "\nQUELLEN:\n" + bullets

    openai.api_key = os.getenv("OPENAI_API_KEY") or sys.exit("OPENAI_API_KEY fehlt")
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=TOKENS,
        temperature=TEMP,
    )
    txt = resp.choices[0].message.content.strip()
    Path("script.txt").write_text(txt)
    print(f"✅  script.txt geschrieben ({len(txt.split())} Wörter)")

if __name__ == "__main__":
    main()
