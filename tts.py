"""
tts.py  –  erzeugt YYYY-MM-DD_briefing.mp3 via Gemini 2.5 Flash TTS
"""

import os, base64, pathlib, sys
from datetime import date
import google.generativeai as genai

# ---------------- Konfiguration -----------------------------------
MODEL_NAME    = "gemini-2.5-flash-preview-tts"
VOICE_NAME    = "puck"         # dt. Stimme
SPEAK_RATE    = 0.95
PITCH         = "+2st"
SCRIPT_FILE   = "script.txt"
OUT_DIR       = pathlib.Path("output")
OUT_FILE      = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"
# -------------------------------------------------------------------

def main() -> None:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        sys.exit("❌ GEMINI_API_KEY fehlt")

    if not pathlib.Path(SCRIPT_FILE).is_file():
        sys.exit("❌ script.txt nicht gefunden – summarize.py ausführen")

    genai.configure(api_key=key)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    model = genai.GenerativeModel(MODEL_NAME)
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
        sys.exit(f"❌ Gemini-API-Fehler: {err}")

    # Audio liegt in Base64 …
    data_b64 = resp.candidates[0].content.parts[0].inline_data.data  # type: ignore[attr-defined]
    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_FILE, "wb") as f:
        f.write(base64.b64decode(data_b64))

    print(f"✅ {OUT_FILE.name} erzeugt")

if __name__ == "__main__":
    main()
