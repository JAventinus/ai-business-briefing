"""
tts.py – erzeugt YYYY-MM-DD_briefing.mp3 via Gemini 2.5 Flash TTS
Kompatibel mit google-generativeai ≥ 0.6.1
"""

import os, sys, base64, pathlib
from datetime import date
import google.generativeai as genai

# ────────── Einstellungen ───────────────────────────────────────────
MODEL_NAME = "gemini-2.5-flash-preview-tts"       # oder …pro-preview-tts
VOICE_NAME = "puck"                               # dt. Stimme
SPEAK_RATE = 0.95
PITCH      = "+2st"

SCRIPT_FILE = "script.txt"
OUT_DIR     = pathlib.Path("output")
OUT_FILE    = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"
# ────────────────────────────────────────────────────────────────────

def fail(msg: str):
    sys.stderr.write(f"❌  {msg}\n")
    sys.exit(1)

def main():
    key = os.getenv("GEMINI_API_KEY") or fail("GEMINI_API_KEY fehlt")
    if not pathlib.Path(SCRIPT_FILE).is_file():
        fail("script.txt nicht gefunden – erst summarize.py ausführen")

    genai.configure(api_key=key)
    model = genai.GenerativeModel(MODEL_NAME)

    text = pathlib.Path(SCRIPT_FILE).read_text(encoding="utf-8")

    try:
        resp = model.generate_content(
            text,
            response_mime_type="audio/mp3",
            audio_config={
                "voice_name":    VOICE_NAME,
                "speaking_rate": SPEAK_RATE,
                "pitch":         PITCH,
            },
        )
    except Exception as err:
        fail(f"Gemini-API-Fehler: {err}")

    try:
        b64_audio = resp.candidates[0].content.parts[0].inline_data.data  # type: ignore[attr-defined]
    except (AttributeError, IndexError):
        fail("Antwortformat unerwartet – prüfe Modellnamen & Key")

    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_bytes(base64.b64decode(b64_audio))
    kb = OUT_FILE.stat().st_size // 1024
    print(f"✅  {OUT_FILE.name} gespeichert ({kb} KB)")

if __name__ == "__main__":
    main()
