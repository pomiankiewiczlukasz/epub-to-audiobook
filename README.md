# EPUB to Audiobook

A simple local Python tool for converting EPUB books into audiobooks using the open-source Kokoro TTS engine.

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
```

## Features 

EPUB chapter extraction
HTML/text cleaning
Local open-source TTS with Kokoro
English male voice (am_michael)
Individual audio files per chapter
FFmpeg audiobook assembly
Resumable generation — existing chapters are skipped


## Requirements

Python 3.12+
FFmpeg
Kokoro TTS


## Installation

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install kokoro ebooklib beautifulsoup4 soundfile numpy tqdm

Make sure FFmpeg is installed:

ffmpeg -version


## Usage

Place your EPUB file at:

data/book.epub

Then run:

python src/audiobook.py

Generated chapter audio files are saved to:

output/chapters/

They can be combined into a single audiobook using FFmpeg.

## Voice

The project currently uses the Kokoro English male voice:

am_michael

## Notes

This project is intended for personal use with legally obtained EPUB files.

Source EPUB files and generated audio are excluded from Git.

