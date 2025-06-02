"""
tts.py – erzeugt YYYY-MM-DD_briefing.mp3 mit Google Cloud TTS
Stimme: de-DE-Neural2-D (m) oder de-DE-Neural2-B (w)
"""

import os, pathlib, sys
from datetime import date
from google.cloud import texttospeech

# ---------- Konfiguration ----------------------------------------------------
VOICE      = "de-DE-Neural2-D"   # z. B. Neural2-B, Neural2-C …
SPEAK_RATE = 0.95
PITCH      = 2.0                 # Halbtonschritte
SCRIPT     = "script.txt"
OUT_DIR    = pathlib.Path("output")
OUT_FILE   = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"
# -----------------------------------------------------------------------------

def fail(msg: str):
    sys.stderr.write(f"❌  {msg}\n")
    sys.exit(1)

def main():
    if not pathlib.Path(SCRIPT).is_file():
        fail("script.txt fehlt – erst summarize.py ausführen.")

    # Client authentifiziert sich automatisch über GDRIVE_CREDENTIALS-JSON
    client = texttospeech.TextToSpeechClient()

    text = pathlib.Path(SCRIPT).read_text(encoding="utf-8")
    input_cfg  = texttospeech.SynthesisInput(text=text)
    voice_cfg  = texttospeech.VoiceSelectionParams(
        language_code="de-DE",
        name=VOICE
    )
    audio_cfg  = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=SPEAK_RATE,
        pitch=PITCH
    )

    resp = client.synthesize_speech(
        input=input_cfg,
        voice=voice_cfg,
        audio_config=audio_cfg
    )

    OUT_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_bytes(resp.audio_content)
    kb = OUT_FILE.stat().st_size // 1024
    print(f"✅  {OUT_FILE.name} gespeichert ({kb} KB)")

if __name__ == "__main__":
    main()
