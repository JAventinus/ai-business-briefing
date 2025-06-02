name: Daily AI Business Briefing

on:
  # 05 : 30 CEST  (03 : 30 UTC)
  schedule:
    - cron: '30 3 * * *'
  workflow_dispatch:        # manueller Start möglich

jobs:
  build:
    runs-on: ubuntu-latest

    # ▸ alle Secrets als ENV-Variablen freigeben
    env:
      GEMINI_API_KEY:  ${{ secrets.GEMINI_API_KEY }}
      OPENAI_API_KEY:  ${{ secrets.OPENAI_API_KEY }}

    steps:
      # ────────────────────────── Code holen
      - name: Checkout repo
        uses: actions/checkout@v4

      # ────────────────────────── Python 3.11 bereitstellen
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      # ────────────────────────── Abhängigkeiten installieren
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install --upgrade google-generativeai     # erzwingt ≥ 0.6.x (TTS-fähig)
          pip install -r requirements.txt

      # ────────────────────────── News sammeln & bewerten
      - name: Crawl & score news
        run: python crawl.py

      # ────────────────────────── Podcast-Script erzeugen
      - name: Build podcast script
        run: python summarize.py

      # ────────────────────────── Text-to-Speech  (Gemini 2.5 Flash)
      - name: Generate MP3 with Gemini TTS
        run: python tts.py          # legt output/YYYY-MM-DD_briefing.mp3 an

      # ────────────────────────── Upload nach Google Drive
      - name: Upload MP3 to Google Drive
        uses: willo32/google-drive-upload-action@v1
        with:
          target:           output/*.mp3
          parent_folder_id: ${{ secrets.GOOGLE_DRIVE_FOLDER }}
          credentials:      ${{ secrets.GDRIVE_CREDENTIALS }}
