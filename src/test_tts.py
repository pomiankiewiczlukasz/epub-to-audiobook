import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from kokoro import KPipeline
import soundfile as sf


# Load EPUB
book = epub.read_epub("book.epub")

# Extract text from the first document
text = ""

for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_DOCUMENT:
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(" ", strip=True)
        if len(text) > 200:
            break

print("Text sample:")
print(text[:1000])

# Kokoro
pipeline = KPipeline(lang_code="a")

# Generate first ~1000 characters
sample = text[:1000]

generator = pipeline(sample, voice="am_michael")

for i, (gs, ps, audio) in enumerate(generator):
    sf.write("test.wav", audio, 24000)
    print("Audio generated: test.wav")
    break