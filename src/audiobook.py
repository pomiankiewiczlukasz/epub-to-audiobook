import argparse
import re
import subprocess
from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from docx import Document
from kokoro import KPipeline
import soundfile as sf
import numpy as np
from tqdm import tqdm


VOICE = "am_michael"
SAMPLE_RATE = 24000

PIPER_MODEL = Path("de_DE-thorsten-high.onnx")

OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# EPUB
# ---------------------------------------------------------------------------

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav"]):
        tag.decompose()

    paragraphs = []

    for element in soup.find_all(["p", "h1", "h2", "h3"]):
        text = element.get_text(" ", strip=True)

        if text:
            paragraphs.append(text)

    text = "\n\n".join(paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def get_toc_links(book):
    links = []

    def extract(items):
        for item in items:
            if isinstance(item, epub.Link):
                links.append(item.href.split("#")[0])
            elif isinstance(item, tuple):
                extract(item)
            elif isinstance(item, list):
                extract(item)

    extract(book.toc)

    return links


def get_chapters(epub_file):
    book = epub.read_epub(str(epub_file))

    items_by_href = {}

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            items_by_href[item.get_name()] = item

    toc_links = get_toc_links(book)

    chapters = []

    for href in toc_links:
        item = items_by_href.get(href)

        if item is None:
            continue

        text = clean_text(item.get_content())

        if len(text) <= 200:
            continue

        first_line = text.splitlines()[0].strip()

        if re.fullmatch(r"\d+", first_line):
            chapters.append(text)

    return chapters


def generate_kokoro_audio(pipeline, text, output_file):
    generator = pipeline(
        text,
        voice=VOICE,
        speed=1.0,
    )

    audio_chunks = []

    for _, _, audio in tqdm(
        generator,
        desc="Generating audio",
        unit="chunk",
    ):
        audio_chunks.append(audio)

    if audio_chunks:
        audio = np.concatenate(audio_chunks)
        sf.write(output_file, audio, SAMPLE_RATE)


def process_epub(input_file):
    output_dir = OUTPUT_DIR / "chapters"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Reading EPUB...")
    chapters = get_chapters(input_file)

    print(f"Found {len(chapters)} chapters.")

    print("Loading Kokoro...")
    pipeline = KPipeline(lang_code="a")

    for i, text in enumerate(chapters, start=1):
        output_file = output_dir / f"chapter_{i:03d}.wav"

        if output_file.exists():
            print(f"Skipping chapter {i}: already exists")
            continue

        print(f"\nGenerating chapter {i}...")
        generate_kokoro_audio(pipeline, text, output_file)

        print(f"Saved: {output_file}")

    print("\nEPUB done!")


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

def extract_docx(docx_file):
    document = Document(docx_file)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    text = "\n\n".join(paragraphs)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def generate_piper_audio(text, output_file):
    if not PIPER_MODEL.exists():
        raise FileNotFoundError(
            f"Piper model not found: {PIPER_MODEL}"
        )

    process = subprocess.Popen(
        [
            "piper",
            "--model",
            str(PIPER_MODEL),
            "--output_file",
            str(output_file),
        ],
        stdin=subprocess.PIPE,
        text=True,
    )

    process.communicate(text)

    if process.returncode != 0:
        raise RuntimeError(
            f"Piper failed with exit code {process.returncode}"
        )


def convert_to_mp3(wav_file, mp3_file):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_file),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "128k",
            "-ac",
            "1",
            str(mp3_file),
        ],
        check=True,
    )


def process_docx(input_file):
    output_dir = OUTPUT_DIR / "docx"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Reading DOCX...")
    text = extract_docx(input_file)

    print(f"Extracted {len(text):,} characters.")

    base_name = input_file.stem

    wav_file = output_dir / f"{base_name}.wav"
    mp3_file = output_dir / f"{base_name}.mp3"

    if not wav_file.exists():
        print("Generating German audio with Piper...")
        generate_piper_audio(text, wav_file)
        print(f"Saved: {wav_file}")
    else:
        print(f"WAV already exists: {wav_file}")

    if not mp3_file.exists():
        print("Converting WAV to MP3...")
        convert_to_mp3(wav_file, mp3_file)
        print(f"Saved: {mp3_file}")
    else:
        print(f"MP3 already exists: {mp3_file}")

    print("\nDOCX done!")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert EPUB or DOCX files to audiobook audio."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Input EPUB or DOCX file.",
    )

    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Input file not found: {args.input}"
        )

    suffix = args.input.suffix.lower()

    if suffix == ".epub":
        process_epub(args.input)

    elif suffix == ".docx":
        process_docx(args.input)

    else:
        raise ValueError(
            "Unsupported file type. Use .epub or .docx."
        )


if __name__ == "__main__":
    main()