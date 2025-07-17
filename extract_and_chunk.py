import os
import shutil
import pickle
import re

# --- Configuration ---
SOURCE_DIRS     = ["about_the_fed_pages", "faq_pages"]
OUTPUT_DIR      = "chunks"
CHUNK_META_FILE = "chunk_data.pkl"

# Chunking parameters
CHUNK_SIZE = 200    # words per chunk
OVERLAP    = 50     # words
MIN_WORDS  = 20     # skip fragments smaller than this

# --- Cleanup old outputs ---
if os.path.exists(OUTPUT_DIR):
    print(f"🔄 Removing existing '{OUTPUT_DIR}' directory...")
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

if os.path.exists(CHUNK_META_FILE):
    print(f"🔄 Removing existing metadata file '{CHUNK_META_FILE}'...")
    os.remove(CHUNK_META_FILE)

# --- Utility functions ---
def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    step = chunk_size - overlap
    chunks = []
    for i in range(0, len(words), step):
        chunk = words[i : i + chunk_size]
        if len(chunk) >= MIN_WORDS:
            chunks.append(" ".join(chunk))
    return chunks


def extract_metadata(lines):
    meta = {}
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("<!--") and ln.endswith("-->") and ":" in ln:
            kv = ln[4:-3].strip()
            key, val = kv.split(":", 1)
            meta[key.strip()] = val.strip()
        elif not ln.startswith("<!--"):
            break
    return meta

# --- Main processing ---
all_chunks = []
files = []
for src in SOURCE_DIRS:
    if not os.path.isdir(src):
        print(f"⚠️ Source directory not found, skipping: '{src}'")
        continue
    for fname in os.listdir(src):
        if fname.lower().endswith(".txt"):
            files.append((src, fname))

print(f"📂 Found {len(files)} source files in {SOURCE_DIRS}")

for src, fname in files:
    path = os.path.join(src, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    if len(lines) < 2:
        print(f"⚠️ Skipping malformed file: {fname}")
        continue

    meta = extract_metadata(lines)
    source_url = meta.get('source_url', '')
    if not source_url:
        print(f"⚠️ No source_url header, skipping: {fname}")
        continue

    # Extract content body
    start_idx = next((i for i, ln in enumerate(lines) if not ln.strip().startswith('<!--')), len(lines))
    content = ''.join(lines[start_idx:]).strip()
    if len(content.split()) < MIN_WORDS:
        print(f"⚠️ Content too short, skipping: {fname}")
        continue

    base = fname[:-4]  # drop .txt
    # FAQ pages: split by question blocks
    if src == 'faq_pages':
        # Identify Q&A pairs by lines ending with '?'
        qa_lines = content.splitlines()
        qa_blocks = []
        current = []
        for ln in qa_lines:
            if ln.strip().endswith('?'):
                if current:
                    qa_blocks.append('\n'.join(current).strip())
                current = [ln]
            else:
                current.append(ln)
        if current:
            qa_blocks.append('\n'.join(current).strip())
        chunks = [blk for blk in qa_blocks if len(blk.split()) >= MIN_WORDS]
        chunk_type = 'faq'
    else:
        # Regular chunking for aboutthefed pages
        chunks = split_into_chunks(content)
        chunk_type = 'aboutthefed'

    # Write out chunks
    for i, chunk in enumerate(chunks, start=1):
        out_name = f"{base}_chunk{i}.txt"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write(chunk)
        all_chunks.append({
            'filename': out_name,
            'source':   base,
            'type':     chunk_type,
            'url':      source_url,
            'title':    meta.get('title', ''),
            'date_fetched': meta.get('date_fetched', '')
        })

print(f"✅ Created {len(all_chunks)} chunks in '{OUTPUT_DIR}'")

# --- Save metadata ---
with open(CHUNK_META_FILE, 'wb') as mf:
    pickle.dump(all_chunks, mf)
print(f"🧠 Saved metadata to '{CHUNK_META_FILE}'")
