"""
summarize.py  –  baut Podcast-Skript aus articles.json
• Primär: GPT-4o-mini  (ca. 2 000 Wörter, 15-20 min Audio)
• Fallback 1: GPT-3.5-turbo-16k    (kürzer, ~1 200 Wörter)
• Fallback 2: Mini-Hinweistext     (falls alle Quoten erschöpft)
"""

import json, os, sys, openai, time
from pathlib import Path

PRIMARY_MODEL   = "gpt-4o-mini"
SECONDARY_MODEL = "gpt-3.5-turbo-16k"
TOKENS_PRIMARY  = 2_800     # ~2 000 Wörter
TOKENS_SECOND   = 1_500
TEMP            = 0.4

TEMPLATE = """\
Du bist Redakteur eines deutschsprachigen Podcasts über KI-Geschäftsmodelle.
Nutze die Quellen, um eine ca. {words} Wörter lange Episode zu schreiben:

# Headline
## Intro – 4-5 Sätze
### Top-Stories
### Deep-Dive
### Take-aways
### Call-to-Action
"""

FALLBACK = """\
# AI Business Briefing
## Intro
Heute liegen keine neuen, relevanten Meldungen zu KI-Geschäftsmodellen vor – \
wir melden uns morgen wieder mit frischen Nachrichten.
"""

def load_articles() -> list[dict]:
    if not Path("articles.json").is_file():
        return []
    return json.loads(Path("articles.json").read_text())

def build_prompt(arts: list[dict], words: int) -> str:
    bullets = "\n".join(f"- {a['title']} ({a['url']})" for a in arts[:12])
    return TEMPLATE.format(words=words) + "\n\nQUELLEN HEUTE:\n" + bullets

def call_openai(model: str, prompt: str, tokens: int) -> str | None:
    try:
        resp = openai.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=tokens,
            temperature=TEMP,
        )
        return resp.choices[0].message.content.strip()
    except openai.RateLimitError as e:
        print(f"⚠️  RateLimit ({model}): {e}")
        return None
    except Exception as e:
        print(f"❌  Fehler ({model}): {e}")
        return None

def main():
    arts = load_articles()
    openai.api_key = os.getenv("OPENAI_API_KEY") or sys.exit("OPENAI_API_KEY fehlt")

    if not arts:
        Path("script.txt").write_text(FALLBACK)
        print("ℹ️  Keine Artikel – Fallback-Text geschrieben.")
        return

    # --- Hauptversuch mit GPT-4o-mini
    txt = call_openai(
        PRIMARY_MODEL,
        build_prompt(arts, 2000),
        TOKENS_PRIMARY
    )
    if txt:
        Path("script.txt").write_text(txt)
        print(f"✅  GPT-4o-Skript geschrieben ({len(txt.split())} Wörter)")
        return

    # --- Zweiter Versuch mit GPT-3.5-turbo-16k
    print("🔄  Versuche GPT-3.5-turbo-16k …")
    txt = call_openai(
        SECONDARY_MODEL,
        build_prompt(arts, 1200),
        TOKENS_SECOND
    )
    if txt:
        Path("script.txt").write_text(txt)
        print(f"✅  GPT-3.5-Skript geschrieben ({len(txt.split())} Wörter)")
        return

    # --- Letzter Fallback
    Path("script.txt").write_text(FALLBACK)
    print("⚠️  Beide Modelle nicht verfügbar – Kurzfassung geschrieben.")

if __name__ == "__main__":
    main()
