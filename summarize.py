"""summarize.py – Minimalversion für ersten End-to-End-Test."""
from datetime import date
TEXT = f"""
AI-Business-Briefing {date.today():%Y-%m-%d}

• Heute keine echten News – dies ist eine Platzhalter-Episode,
  um den technischen Workflow zu prüfen.
• Sobald crawl.py und die Prompts fertig sind, erzeugt dieses
  Skript automatisch den vollständigen Podcast-Text.

Ende des Tests.
"""
with open("script.txt", "w", encoding="utf-8") as f:
    f.write(TEXT.strip())
print("✅  script.txt geschrieben")
