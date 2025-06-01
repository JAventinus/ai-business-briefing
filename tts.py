"""
tts.py  –  erzeugt YYYY-MM-DD_briefing.mp3 via Gemini 2.5 Flash TTS
"""

import os, base64, pathlib, sys
from datetime import date
from google import genai

# ---------- Konfiguration ---------------------------------------------------
MODEL_NAME    = "gemini-2.5-flash-preview-tts"
VOICE_NAME    = "puck"       #  dt. Stimme  (weitere: kore, fenrir …)
SPEAK_RATE    = 0.95
PITCH         = "+2st"
SCRIPT_FILE   = "script.txt"
OUT_DIR       = pathlib.Path("output")
OUT_FILE      = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"
# ----------------------------------------------------------------------------

def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("❌  GEMINI_API_KEY fehlt – Secret/ENV setzen.")

    if not pathlib.Path(SCRIPT_FILE).is_file():
        sys.exit("❌  script.txt fehlt – erst summarize.py ausführen.")

    genai_client = genai.Client(api_key=api_key)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    try:
        resp = genai_client.models.generate_content(
            model   = MODEL_NAME,
            contents= text,
            config  = {
                "response_mime_type": "audio/mp3",
                "audio_config": {
                    "voice_name":    VOICE_NAME,
                    "speaking_rate": SPEAK_RATE,
                    "pitch":         PITCH,
                },
            },
        )
    except Exception as err:
        sys.exit(f"❌  Gemini-API-Fehler: {err}")

    audio_b64 = resp.candidates[0].content.parts[0].inline_data.data  # type: ignore
    OUT_DIR.mkdir(exist_ok=True)
    with open(OUT_FILE, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    print(f"✅  {OUT_FILE.name} gespeichert – Workflow fertig.")

if __name__ == "__main__":
    main()
