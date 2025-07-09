import streamlit as st
import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index and metadata
def load_faiss_index_and_metadata():
    index = faiss.read_index("faiss_index.index")
    with open("metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

# Perform search
def search_index(query, index, metadata, top_k=5):
    embedding = model.encode([query])
    distances, indices = index.search(np.array(embedding).astype("float32"), top_k)
    results = []
    for i in indices[0]:
        if i < len(metadata):
            results.append(metadata[i])
    return results

# Load index and metadata
index, metadata = load_faiss_index_and_metadata()

# Streamlit UI
st.set_page_config(page_title="FedBot", page_icon="📊")
st.title("FedBot: Ask About the Fed")
st.markdown("""
Ask questions about the structure, policies, and people behind the U.S. Federal Reserve System.
""")

# Suggested questions
st.markdown("### 🔎 Try a sample question:")
col1, col2 = st.columns(2)
with col1:
    if st.button("What does the Board of Governors do?"):
        st.session_state.query = "What does the Board of Governors do?"
with col2:
    if st.button("Who appoints Federal Reserve Board members?"):
        st.session_state.query = "Who appoints Federal Reserve Board members?"

# Main input
query = st.text_input("\n💬 Your question:", value=st.session_state.get("query", ""))

if query:
    st.markdown("---")
    st.markdown("### 📄 Answer:")
    results = search_index(query, index, metadata)

    for result in results:
        source_url = result.get("url", "")
        st.markdown(f"- [🔗 {source_url}]({source_url})")

        chunk_file = os.path.join("chunks", result["filename"])
        if os.path.exists(chunk_file):
            with open(chunk_file, "r", encoding="utf-8") as f:
                st.write(f.read())
