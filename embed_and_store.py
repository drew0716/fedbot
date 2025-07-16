# embed_and_store.py

import os
import faiss
import pickle
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

CHUNKS_DIR = "chunks"
CHUNK_META_FILE = "chunk_data.pkl"
OUTPUT_DIR = "output"
INDEX_FILE = os.path.join(OUTPUT_DIR, "faiss_index.index")
METADATA_FILE = os.path.join(OUTPUT_DIR, "metadata.pkl")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load Sentence Transformer model
print("🧠 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunk metadata
if not os.path.exists(CHUNK_META_FILE):
    raise FileNotFoundError(f"Chunk metadata file not found: {CHUNK_META_FILE}")

with open(CHUNK_META_FILE, "rb") as f:
    chunk_data = pickle.load(f)

texts = []
metadata = []

print("📦 Reading chunk files...")
for chunk in tqdm(chunk_data):
    file_path = os.path.join(CHUNKS_DIR, chunk["filename"])
    if not os.path.exists(file_path):
        print(f"⚠️ Missing chunk file: {chunk['filename']}")
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()
        if not text:
            continue
        texts.append(text)
        metadata.append({
            "filename": chunk["filename"],
            "source": chunk["source"],
            "type": chunk["type"],
            "url": chunk.get("url", "")
        })

if not texts:
    raise ValueError("❌ No valid text chunks found to embed.")

# Generate embeddings
print("🔍 Generating embeddings...")
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Build FAISS index
print("💾 Building FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index and metadata
print(f"📁 Saving FAISS index to: {os.path.abspath(INDEX_FILE)}")
faiss.write_index(index, INDEX_FILE)

print(f"📁 Saving metadata to: {os.path.abspath(METADATA_FILE)}")
with open(METADATA_FILE, "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ Successfully indexed {len(texts)} chunks.")
