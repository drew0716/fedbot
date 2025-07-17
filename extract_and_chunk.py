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
def load_model():
    print("🧠 Loading embedding model...")
    return SentenceTransformer("all-MiniLM-L6-v2")

# Load chunk metadata
def load_metadata():
    if not os.path.exists(CHUNK_META_FILE):
        raise FileNotFoundError(f"Chunk metadata file not found: {CHUNK_META_FILE}")
    with open(CHUNK_META_FILE, "rb") as f:
        return pickle.load(f)

# Read text chunks and build arrays
def prepare_embeddings(chunk_data, model):
    texts = []
    meta  = []
    for idx, chunk in enumerate(tqdm(chunk_data, desc="Reading chunks")):
        fname = chunk.get("filename")
        path  = os.path.join(CHUNKS_DIR, fname)
        if not os.path.exists(path):
            print(f"⚠️ Missing chunk file: {fname}")
            continue
        text = open(path, "r", encoding="utf-8").read().strip()
        if not text:
            continue
        texts.append(text)
        meta.append({
            "id":       idx,
            "filename": fname,
            "source":   chunk.get("source", ""),
            "type":     chunk.get("type", ""),
            "url":      chunk.get("url", "")
        })
    if not texts:
        raise ValueError("❌ No valid text chunks found to embed.")
    # Generate and normalize embeddings for cosine similarity
    print("🔍 Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(embeddings)
    return embeddings, meta

# Build FAISS index with inner-product
def build_index(embeddings, meta):
    dim = embeddings.shape[1]
    print("💾 Building FAISS index (cosine similarity)...")
    index_flat = faiss.IndexFlatIP(dim)
    index = faiss.IndexIDMap(index_flat)
    ids = np.array([m["id"] for m in meta], dtype=np.int64)
    index.add_with_ids(embeddings, ids)
    return index

# Save index and metadata to disk
def save_output(index, meta):
    print(f"📁 Saving FAISS index to: {os.path.abspath(INDEX_FILE)}")
    faiss.write_index(index, INDEX_FILE)
    print(f"📁 Saving metadata to: {os.path.abspath(METADATA_FILE)}")
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(meta, f)
    faq_cnt   = sum(1 for m in meta if m.get("type") == "faq")
    about_cnt = len(meta) - faq_cnt
    print(f"✅ Indexed {len(meta)} chunks: {about_cnt} 'aboutthefed', {faq_cnt} 'faq'.")

if __name__ == "__main__":
    model       = load_model()
    chunk_data  = load_metadata()
    embeddings, meta = prepare_embeddings(chunk_data, model)
    index       = build_index(embeddings, meta)
    save_output(index, meta)
