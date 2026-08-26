# EPUB to Audiobook

A simple local Python tool for converting EPUB and DOCX books into audiobooks using the open-source Kokoro TTS engine.

## How it works

```text
EPUB
 ↓
Chapter extraction
 ↓
Text cleaning
 ↓
Kokoro TTS
 ↓
WAV files
 ↓
FFmpeg
 ↓
Audiobook MP3


DOCX
 ↓
Text extraction
 ↓
Piper TTS
 ↓
WAV
 ↓
FFmpeg
 ↓
MP3 audiobook

```

## Features 

EPUB chapter extraction
DOCX text extraction
HTML/text cleaning
Local open-source text-to-speech
Kokoro TTS for English
Piper TTS for German
English male voice (am_michael)
German voice (de_DE-thorsten-high)
Individual audio files per EPUB chapter
WAV to MP3 conversion for DOCX
Resumable generation — existing audio files are skipped
No cloud APIs required


## Requirements

Python 3.12+
FFmpeg
Kokoro TTS
Piper TTS


## Installation

Create and activate a virtual environment:

python -m venv .venv
.venv\Scripts\Activate.ps1

Install the dependencies:

pip install kokoro ebooklib beautifulsoup4 soundfile numpy tqdm python-docx piper-tts

Make sure FFmpeg is installed:

ffmpeg -version
German voice

Download the German Piper voice:

python -m piper.download_voices de_DE-thorsten-high

This downloads:

de_DE-thorsten-high.onnx
de_DE-thorsten-high.onnx.json


## Usage

EPUB

Place the EPUB file at:

data/book.epub

Then run:

python src/audiobook.py --input "data\book.epub"

Generated chapter audio files are saved to:

output/chapters/


DOCX

Place the Word document in the data directory, for example:

data/DE Text.docx

Then run:

python src/audiobook.py --input "data\DE Text.docx"

The generated files are saved to:

output/docx/

For example:

output/docx/
├── DE Text.wav
└── DE Text.mp3

## Voices

English

Kokoro:

am_michael


German

Piper:

de_DE-thorsten-high


## Notes

This project is intended for personal use with legally obtained EPUB and DOCX files.

Source books and generated audio are excluded from Git.



