"""
tts.py – erzeugt AI-Business-Briefing als MP3 mit Datum im Dateinamen
--------------------------------------------------------------------
• liest script.txt
• ruft Gemini 2.5 Flash-TTS auf
• legt YYYY-MM-DD_briefing.mp3 in output/ ab
"""

import os, base64, pathlib, sys
from datetime import date
import google.generativeai as genai

# ---------- Konfiguration ---------------------------------------------------
MODEL_NAME    = "gemini-2.5-flash-preview-tts"   # alternativ: gemini-2.5-pro-preview-tts
VOICE_NAME    = "puck"                           # dt. Stimme (z. B. kore, fenrir, …)
SPEAKING_RATE = 0.95
PITCH         = "+2st"
SCRIPT_FILE   = "script.txt"
OUTPUT_DIR    = pathlib.Path("output")
FILENAME      = f"{date.today():%Y-%m-%d}_briefing.mp3"
OUTPUT_FILE   = OUTPUT_DIR / FILENAME
# ---------------------------------------------------------------------------

def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("❌  GEMINI_API_KEY fehlt (GitHub-Secret oder ENV-Var setzen).")

    if not pathlib.Path(SCRIPT_FILE).is_file():
        sys.exit("❌  script.txt nicht gefunden – erst summarize.py ausführen.")

    genai.configure(api_key=api_key)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    print("⏳  Konvertiere Text → MP3 …")
    try:
        resp = genai.generate_content(
            model            = MODEL_NAME,
            contents         = [text],
            response_mime_type = "audio/mp3",
            audio_config     = {
                "voice_name":    VOICE_NAME,
                "speaking_rate": SPEAKING_RATE,
                "pitch":         PITCH,
            },
        )
        audio_b64 = (
            resp.candidates[0]
                .content.parts[0]
                .inline_data.data        # type: ignore[attr-defined]
        )
    except Exception as e:
        sys.exit(f"❌  Gemini-API-Fehler: {e}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(base64.b64decode(audio_b64))

    size_kb = OUTPUT_FILE.stat().st_size // 1024
    print(f"✅  {OUTPUT_FILE.name} gespeichert ({size_kb} KB)")

if __name__ == "__main__":
    main()
