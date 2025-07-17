import os
import faiss
import pickle
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Directories and files
CHUNKS_DIR      = "chunks"
CHUNK_META_FILE = "chunk_data.pkl"
OUTPUT_DIR      = "output"
INDEX_FILE      = os.path.join(OUTPUT_DIR, "faiss_index.index")
METADATA_FILE   = os.path.join(OUTPUT_DIR, "metadata.pkl")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load embedding model
print("🧠 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunk metadata
if not os.path.exists(CHUNK_META_FILE):
    raise FileNotFoundError(f"Chunk metadata file not found: {CHUNK_META_FILE}")
with open(CHUNK_META_FILE, "rb") as f:
    chunk_data = pickle.load(f)

# Prepare texts and metadata lists
texts = []
meta  = []

print("📦 Reading chunk files...")
for idx, chunk in enumerate(tqdm(chunk_data, desc="Chunks")):
    filename = chunk.get("filename")
    file_path = os.path.join(CHUNKS_DIR, filename)
    if not os.path.exists(file_path):
        print(f"⚠️ Missing chunk file: {filename}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        continue

    texts.append(text)
    meta.append({
        "id":       idx,
        "filename": filename,
        "source":   chunk.get("source", ""),
        "type":     chunk.get("type", ""),
        "url":      chunk.get("url", "")
    })

if not texts:
    raise ValueError("❌ No valid text chunks found to embed.")

# Generate embeddings
print("🔍 Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings, dtype="float32")

# Build FAISS index with ID mapping
print("💾 Building FAISS index with ID mapping...")
dim   = embeddings.shape[1]
index_flat = faiss.IndexFlatL2(dim)
index      = faiss.IndexIDMap(index_flat)
ids        = np.array([m["id"] for m in meta], dtype=np.int64)
index.add_with_ids(embeddings, ids)

# Save index
print(f"📁 Saving FAISS index to: {os.path.abspath(INDEX_FILE)}")
faiss.write_index(index, INDEX_FILE)

# Save metadata
print(f"📁 Saving metadata to: {os.path.abspath(METADATA_FILE)}")
with open(METADATA_FILE, "wb") as f:
    pickle.dump(meta, f)

# Summary
faq_count    = sum(1 for m in meta if m["type"] == "faq")
about_count  = len(meta) - faq_count
print(f"✅ Indexed {len(meta)} chunks: {about_count} 'aboutthefed' and {faq_count} 'faq'.")
