import os
import pickle

SOURCE_DIR = "about_the_fed_pages"
OUTPUT_DIR = "chunks"
CHUNK_META_FILE = "chunk_data.pkl"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHUNK_SIZE = 1000  # words
OVERLAP = 200      # words

all_chunks = []

def split_into_chunks(text, chunk_size, overlap):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if len(chunk.split()) > 50:  # skip tiny ones
            chunks.append(chunk)
    return chunks

files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
if not files:
    raise FileNotFoundError(f"No .txt files found in {SOURCE_DIR}")

print(f"📂 Chunking {len(files)} source files...")

for filename in files:
    filepath = os.path.join(SOURCE_DIR, filename)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines or len(lines) < 2:
        print(f"⚠️ Skipping empty or malformed file: {filename}")
        continue

    # Extract URL from the first line
    url_line = lines[0].strip()
    if not url_line.startswith("<!--") or not url_line.endswith("-->"):
        print(f"⚠️ Skipping file without valid source URL comment: {filename}")
        continue

    source_url = url_line.replace("<!--", "").replace("-->", "").strip()
    content = "".join(lines[1:]).strip()

    if len(content.split()) < 100:
        print(f"⚠️ Skipping short file: {filename}")
        continue

    base_name = filename.replace(".txt", "")
    chunks = split_into_chunks(content, CHUNK_SIZE, OVERLAP)

    for i, chunk in enumerate(chunks):
        out_name = f"{base_name}_chunk{i+1}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        with open(out_path, "w", encoding="utf-8") as out:
            out.write(chunk)

        all_chunks.append({
            "filename": out_name,
            "source": base_name,
            "type": "aboutthefed",
            "url": source_url
        })

print(f"✅ Created {len(all_chunks)} total chunks.")

# Save chunk metadata
with open(CHUNK_META_FILE, "wb") as f:
    pickle.dump(all_chunks, f)

print(f"🧠 Metadata saved to {CHUNK_META_FILE}")
