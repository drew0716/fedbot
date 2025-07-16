import os
import pickle

SOURCE_DIRS = ["about_the_fed_pages", "faq_pages"]
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

def extract_metadata(lines):
    metadata = {}
    for line in lines:
        line = line.strip()
        if line.startswith("<!--") and line.endswith("-->") and ":" in line:
            key_value = line.replace("<!--", "").replace("-->", "").strip()
            key, val = key_value.split(":", 1)
            metadata[key.strip()] = val.strip()
        elif not line.startswith("<!--"):
            break  # Stop once actual content starts
    return metadata

files = []
for sdir in SOURCE_DIRS:
    if not os.path.exists(sdir):
        continue
    for f in os.listdir(sdir):
        if f.endswith(".txt"):
            files.append((sdir, f))

if not files:
    raise FileNotFoundError(f"No .txt files found in {SOURCE_DIRS}")

print(f"📂 Chunking {len(files)} source files from {SOURCE_DIRS}...")

for sdir, filename in files:
    filepath = os.path.join(sdir, filename)
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines or len(lines) < 2:
        print(f"⚠️ Skipping empty or malformed file: {filename}")
        continue

    metadata = extract_metadata(lines)
    source_url = metadata.get("source_url", "")
    if not source_url:
        print(f"⚠️ Skipping file without source_url: {filename}")
        continue

    content_start_idx = next((i for i, line in enumerate(lines) if not line.strip().startswith("<!--")), len(lines))
    content = "".join(lines[content_start_idx:]).strip()

    if len(content.split()) < 100:
        print(f"⚠️ Skipping short file: {filename}")
        continue

    base_name = filename.replace(".txt", "")
    chunks = split_into_chunks(content, CHUNK_SIZE, OVERLAP)

chunk_type = "faq" if "faq" in sdir else "aboutthefed"
for i, chunk in enumerate(chunks):
    out_name = f"{base_name}_chunk{i+1}.txt"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    with open(out_path, "w", encoding="utf-8") as out:
        out.write(chunk)

    all_chunks.append({
        "filename": out_name,
        "source": base_name,
        "type": chunk_type,
        "url": source_url,
        "title": metadata.get("title", "Untitled"),
        "date_fetched": metadata.get("date_fetched", None)
    })

print(f"✅ Created {len(all_chunks)} total chunks.")

# Save chunk metadata
with open(CHUNK_META_FILE, "wb") as f:
    pickle.dump(all_chunks, f)

print(f"🧠 Metadata saved to {CHUNK_META_FILE}")
