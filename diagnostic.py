import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# Paths to your index and metadata
INDEX_PATH = "output/faiss_index.index"
META_PATH  = "output/metadata.pkl"

def main():
    # 1. Load metadata and FAISS index
    meta  = pickle.load(open(META_PATH, "rb"))
    index = faiss.read_index(INDEX_PATH)

    # 2. Counts
    total_meta  = len(meta)
    total_index = index.ntotal
    faq_count   = sum(1 for m in meta if m.get("type") == "faq")
    about_count = total_meta - faq_count

    print(f"Total metadata entries : {total_meta}")
    print(f"Total index vectors    : {total_index}")
    print(f"FAQ chunks             : {faq_count}")
    print(f"About‑the‑Fed chunks   : {about_count}\n")

    # 3. Retrieval test
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query = "Is there a new VIP dining room?"
    q_emb = model.encode([query]).astype("float32")

    distances, ids = index.search(q_emb, 10)
    print(f"Top 10 search results for: “{query}”\n")
    for dist, idx in zip(distances[0], ids[0]):
        if idx < 0:
            continue
        entry = meta[idx]
        print(f"- Distance: {dist:.4f} | Type: {entry['type']} | URL: {entry['url']}")

if __name__ == "__main__":
    main()
