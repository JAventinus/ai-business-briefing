"""
tts.py  –  wandelt script.txt in briefing.mp3
• zerlegt Text in max 4 500-Byte-Chunks (TTS-Limit 5 000)
• ruft Google Cloud TTS pro Chunk auf
• führt alle Audios zusammen
"""

import os, sys, base64, pathlib, re, math
from datetime import date
from google.cloud import texttospeech

VOICE      = "de-DE-Neural2-D"
RATE       = 0.95
PITCH      = 2.0
MAX_BYTES  = 4500          # konservativ unter 5 000

SCRIPT     = "script.txt"
OUT_DIR    = pathlib.Path("output")
OUT_FILE   = OUT_DIR / f"{date.today():%Y-%m-%d}_briefing.mp3"

def fail(msg):
    sys.stderr.write(f"❌  {msg}\n"); sys.exit(1)

def chunks_by_bytes(text, lim):
    words, chunk, size = text.split(), [], 0
    for w in words:
        b = len((w + " ").encode("utf-8"))
        if size + b > lim:
            yield " ".join(chunk)
            chunk, size = [], 0
        chunk.append(w); size += b
    if chunk:
        yield " ".join(chunk)

def synthesize(client, txt):
    req = dict(
        input=texttospeech.SynthesisInput(text=txt),
        voice=texttospeech.VoiceSelectionParams(
            language_code="de-DE", name=VOICE),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=RATE, pitch=PITCH)
    )
    return client.synthesize_speech(**req).audio_content

def main():
    if not pathlib.Path(SCRIPT).is_file():
        fail("script.txt fehlt – erst summarize.py ausführen")

    full = pathlib.Path(SCRIPT).read_text(encoding="utf-8").strip()
    if len(full.encode()) <= 500: fail("script.txt extrem kurz – abgebrochen")

    client = texttospeech.TextToSpeechClient()

    OUT_DIR.mkdir(exist_ok=True)
    tmp_files = []

    for i, chunk in enumerate(chunks_by_bytes(full, MAX_BYTES), 1):
        audio = synthesize(client, chunk)
        part = OUT_DIR / f"part_{i:02d}.mp3"
        part.write_bytes(audio)
        tmp_files.append(part)
        print(f"🔹  Chunk {i} → {part.name} ({len(audio)//1024} KB)")

    # concat via simple binary append (MP3 frames, gleiche Params)
    with open(OUT_FILE, "wb") as out:
        for p in tmp_files:
            out.write(p.read_bytes())
    print(f"✅  {OUT_FILE.name} fertig ({OUT_FILE.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
