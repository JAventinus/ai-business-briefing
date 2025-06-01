"""
tts.py – erzeugt briefing.mp3 aus script.txt mit Gemini 2.5 Flash TTS
--------------------------------------------------------------------
Voraussetzungen
• Umgebungsvariable  GEMINI_API_KEY  (Repo-Secret in GitHub Actions)
• Datei  script.txt  (wird von summarize.py erzeugt)
• Paket  google-generativeai  (steht in requirements.txt)

Ausgabe
• output/briefing.mp3   – News-Podcast (≈ 15–20 min)

Aufruf lokal:
    export GEMINI_API_KEY="sk-..."      # einmalig in der Shell
    python tts.py                       # schreibt briefing.mp3
"""

import os
import base64
import pathlib
import sys
import google.generativeai as genai

# ----------------------------------------------------------------------
# Konfiguration – passe bei Bedarf nur die Konstanten DICHTER unten an
# ----------------------------------------------------------------------
MODEL_NAME      = "gemini-2.5-flash-preview-tts"   # oder gemini-2.5-pro-preview-tts
VOICE_NAME      = "puck"                           # dt. weiblich; weitere: kore, fenrir …
SPEAKING_RATE   = 0.95                             # 0.9–1.05 klingt für News am besten
PITCH           = "+2st"                           # semitone shift; 0 = neutral
SCRIPT_FILE     = "script.txt"
OUTPUT_DIR      = pathlib.Path("output")
OUTPUT_FILE     = OUTPUT_DIR / "briefing.mp3"
# ----------------------------------------------------------------------

def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("❌  GEMINI_API_KEY fehlt (als ENV-Var oder GitHub-Secret).")

    if not pathlib.Path(SCRIPT_FILE).is_file():
        sys.exit(f"❌  {SCRIPT_FILE} nicht gefunden. Vorher summarize.py ausführen.")

    genai.configure(api_key=api_key)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    print("⏳  Konvertiere Text → Audio …")
    try:
        response = genai.generate_content(
            model=MODEL_NAME,
            contents=[text],
            response_mime_type="audio/mp3",
            audio_config={
                "voice_name": VOICE_NAME,
                "speaking_rate": SPEAKING_RATE,
                "pitch": PITCH,
            },
        )
    except Exception as err:
        sys.exit(f"❌  Gemini-API-Fehler: {err}")

    # API liefert Base64-kodierte Bytes
    try:
        audio_b64 = (
            response.candidates[0]
            .content.parts[0]
            .inline_data.data  # type: ignore[attr-defined]
        )
    except (AttributeError, IndexError):
        sys.exit("❌  Unerwartetes Antwortformat – Prüfe Modellnamen & Key.")

    audio_bytes = base64.b64decode(audio_b64)

    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "wb") as f:
        f.write(audio_bytes)

    size_kb = OUTPUT_FILE.stat().st_size // 1024
    print(f"✅  {OUTPUT_FILE} gespeichert ({size_kb} KB)")

if __name__ == "__main__":
    main()
