"""
tts.py  –  Daily-Podcast als MP3 mit Datum
-----------------------------------------
• nimmt script.txt
• nutzt Gemini 2.5 Flash (Single-Speaker-TTS)
• legt YYYY-MM-DD_briefing.mp3 in output/ ab
"""

import os
import base64
import pathlib
import sys
from datetime import date

import google.generativeai as genai

# ────────── Konfiguration anpassen ────────────────────────────────────────────
MODEL_NAME   = "gemini-2.5-flash-preview-tts"   # oder ...pro-preview-tts
VOICE_NAME   = "puck"                           # dt. Stimme; weitere: kore, fenrir
SPEAK_RATE   = 0.95
PITCH        = "+2st"

SCRIPT_FILE  = "script.txt"
OUT_DIR      = pathlib.Path("output")
OUT_FILE     = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"
# ───────────────────────────────────────────────────────────────────────────────

def fail(msg: str) -> None:
    sys.stderr.write(f"❌  {msg}\n")
    sys.exit(1)

def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY") or fail("GEMINI_API_KEY fehlt.")
    if not pathlib.Path(SCRIPT_FILE).is_file():
        fail("script.txt nicht gefunden – vorher summarize.py ausführen.")

    # SDK konfigurieren
    genai.configure(api_key=api_key)

    # Text laden
    with open(SCRIPT_FILE, encoding="utf-8") as f:
        text = f.read()

    # Modell instanziieren
    model = genai.GenerativeModel(MODEL_NAME)

    # TTS-Aufruf
    try:
        resp = model.generate_content(
            text,
            response_mime_type="audio/mp3",
            audio_config={
                "voice_name": VOICE_NAME,
                "speaking_rate": SPEAK_RATE,
                "pitch": PITCH,
            },
        )
    except Exception as err:
        fail(f"Gemini-API-Fehler: {err}")

    # Base64-Audio entpacken
    try:
        b64_audio = resp.candidates[0].content.parts[0].inline_data.data  # type: ignore
    except (AttributeError, IndexError):
        fail("Antwortformat unerwartet – Prüfe Modellnamen & Key.")

    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_FILE, "wb") as f:
        f.write(base64.b64decode(b64_audio))

    size_kb = OUT_FILE.stat().st_size // 1024
    print(f"✅  {OUT_FILE.name} gespeichert ({size_kb} KB)")

if __name__ == "__main__":
    main()
