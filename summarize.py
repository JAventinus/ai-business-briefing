"""
summarize.py – fasst articles.json in ein Podcast-Skript
• nutzt OpenAI GPT-4o 32k
• erzeugt script.txt  (≈ 2 000 Wörter, 15-20 min Audio)
"""

import json, os, textwrap, openai, sys, datetime
from pathlib import Path

MODEL = "gpt-4o-mini"        # günstig + lang
TOKENS = 3_000               # max. Output
TEMPERATURE = 0.4

SYSTEM_PROMPT = """\
Du bist Redakteur eines täglichen deutschsprachigen Podcasts für KI-Geschäftsmodelle.
Deine Hörer sind Manager und Gründer, die mit KI Geld verdienen wollen.
Erstelle eine 15-20-minütige Episode (~2 000 Wörter).

Format:
# Headline (max 12 Wörter)
## Intro – 4-5 Sätze, warum diese Episode wichtig ist
### Top-Stories
* Story 1: knackige Zusammenfassung (max 120 Wörter) → „Warum ist das relevant?“
* Story 2: …
### Deep-Dive
Abschnitt      | Inhalt (5-6 Sätze)
---------------|--------------------------------------------------------------
Markttrends    | ...
Neue Player    | ...
Funding/M&A    | ...
Risiken&Reg    | ...
### Take-aways
1. wichtigste Lehre
2. …
### Call-to-Action
"""

def load_articles() -> list[dict]:
    if not Path("articles.json").is_file():
        sys.exit("articles.json fehlt – erst crawl.py ausführen")
    data = json.loads(Path("articles.json").read_text())
    if not data:
        sys.exit("Keine Artikel gefunden.")
    return data

def build_prompt(arts: list[dict]) -> str:
    bullets = "\n".join(
        f"- {a['title']} ({a['url']})" for a in arts[:12]
    )
    return SYSTEM_PROMPT + "\n\nRELEVANTE QUELLEN HEUTE:\n" + bullets

def main() -> None:
    arts = load_articles()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        sys.exit("OPENAI_API_KEY fehlt.")

    prompt = build_prompt(arts)
    print("⏳  GPT-Zusammenfassung …")
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
        ],
        max_tokens=TOKENS,
        temperature=TEMPERATURE,
    )
    text = resp.choices[0].message.content.strip()
    Path("script.txt").write_text(text)
    print(f"✅  script.txt geschrieben ({len(text.split())} Wörter)")

if __name__ == "__main__":
    main()
