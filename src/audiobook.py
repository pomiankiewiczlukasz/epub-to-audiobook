import re
from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from kokoro import KPipeline
import soundfile as sf
import numpy as np
from tqdm import tqdm


EPUB_FILE = Path("data/book.epub")
OUTPUT_DIR = Path("output/chapters")

VOICE = "am_michael"
SAMPLE_RATE = 24000


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


def get_chapters():
    book = epub.read_epub(str(EPUB_FILE))

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

        # Keep only numbered chapters: 1, 2, ..., 10
        if re.fullmatch(r"\d+", first_line):
            chapters.append(text)

    return chapters


def generate_audio(pipeline, text, output_file):
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


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Reading EPUB...")
    chapters = get_chapters()

    print(f"Found {len(chapters)} chapters.")

    print("Loading Kokoro...")
    pipeline = KPipeline(lang_code="a")

    for i, text in enumerate(chapters, start=1):
        output_file = OUTPUT_DIR / f"chapter_{i:03d}.wav"

        if output_file.exists():
            print(f"Skipping chapter {i}: already exists")
            continue

        print(f"\nGenerating chapter {i}...")
        generate_audio(pipeline, text, output_file)

        print(f"Saved: {output_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()