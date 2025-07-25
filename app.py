import os
import pickle
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
import anthropic

# Anthropic API key
api_key = st.secrets.get("ANTHROPIC_API_KEY")
if not api_key:
    st.error("Anthropic API key not found. Set ANTHROPIC_API_KEY in your environment.")
    st.stop()

client = anthropic.Anthropic(api_key=api_key)

# App config and styles
st.set_page_config(page_title="FedBot: About the Fed Q&A", layout="wide")
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1a1a1a;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.6rem;
    }
    .suggestion-button button {
        width: 100%;
        height: 100%;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        border-radius: 6px;
        border: 1px solid #aebac6;
        background-color: #f2f6f9;
        color: #003366;
        transition: background-color 0.2s ease;
        text-align: center;
        font-weight: 500;
    }
    .suggestion-button button:hover {
        background-color: #e6eff6;
    }
    .sample-question-tile {
        border: 1px solid #c5d0dd;
        border-radius: 6px;
        padding: 0.75rem;
        background-color: #f8fafc;
        font-size: 1rem;
        font-weight: 500;
        color: #003366;
        margin-bottom: 0.5rem;
        height: 100%;
    }
    footer {
        font-size: 0.85rem;
        color: #666;
        text-align: center;
        padding-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("FedBot: About the Fed Q&A")

# 📅 Show last updated date
if os.path.exists("last_updated.txt"):
    with open("last_updated.txt", "r") as f:
        last_updated = f.read().strip()
    st.caption(f"📅 Last updated: {last_updated}")

# Load model, index, and metadata
@st.cache_resource
def load_assets():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index_path = os.path.join("output", "faiss_index.index")
    metadata_path = os.path.join("output", "metadata.pkl")
    index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)
    return model, index, metadata

model, index, metadata = load_assets()

# Initialize session state
if "question_input" not in st.session_state:
    st.session_state.question_input = ""

# --- Question Input ---
question = st.text_input(
    "Type your question:",
    value=st.session_state.question_input,
    placeholder="e.g., How does the Federal Reserve influence interest rates?",
    key="main_input"
)

# --- Suggested Questions ---
st.markdown("#### Explore Topics")
important_questions = [
    "What is the purpose of the Federal Reserve?",
    "How is the Federal Reserve structured?",
    "What is the role of the FOMC?",
    "How does the Fed supervise banks?"
]

q_cols = st.columns(2)
for i, q in enumerate(important_questions):
    with q_cols[i % 2]:
        if st.button(q, key=f"btn_{i}"):
            st.session_state.question_input = q
            st.rerun()

# --- Search and Answer ---
if question:
    q_embedding = model.encode([question]).astype("float32")
    faiss.normalize_L2(q_embedding)  # normalize for cosine similarity
    D, I = index.search(q_embedding, k=10)

    context = ""
    sources = []
    added = 0

    for idx in I[0]:
        meta_entry = metadata[idx]
        chunk_type = meta_entry.get("type", "aboutthefed")
        chunk_file = os.path.join("chunks", meta_entry["filename"])
        if not os.path.exists(chunk_file):
            continue
        with open(chunk_file,  "r", encoding="utf-8") as cf:
            content = cf.read()
        context += f"\n---\n{content}"

        # Build display title
        source_key = meta_entry.get("source", "").replace(".txt", "")
        if chunk_type == "aboutthefed":
            title = f"About the Fed: {source_key.replace('_', ' ').title()}"
        else:
            title = "FAQ: " + (meta_entry.get("title") or "Federal Reserve FAQ")

        sources.append((title, meta_entry.get("url")))
        added += 1
        if added >= 5:
            break

    if not context:
        st.warning("No relevant content found for your question.")
    else:
        system_prompt = (
            "You are a helpful assistant answering questions using verified information from the United States Federal Reserve. "
            "Your answers are based only on two official sources: the 'About the Fed' section and the official FAQ pages at federalreserve.gov. "
            "Always provide citations to the source(s) used. "
            "If the answer is not present in the context, say you could not find it."
        )
        user_prompt = f"""Answer the following question using only the context below. If the information isn't available, respond accordingly.

Context:
{context}

Question: {question}
"""

        with st.spinner("Retrieving answer..."):
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

        st.markdown("### Answer")
        st.markdown(response.content[0].text)

        st.markdown("### Sources")
        for name, url in sources:
            if url:
                st.markdown(f"- [{name}]({url})")
            else:
                st.markdown(f"- {name}")

# --- Footer ---
st.markdown("""
---
<footer>
  This tool uses public data from federalreserve.gov and Anthropic's Claude 3 model to provide answers based on "About the Fed" and "FAQs" content.<br>
  <strong>Disclaimer:</strong> This tool is not affiliated with or endorsed by the Federal Reserve System.
</footer>
""", unsafe_allow_html=True)

# 🔁 Show force redeploy timestamp
if os.path.exists("force_redeploy.txt"):
    with open("force_redeploy.txt", "r") as f:
        refreshed = f.read().strip()
    st.caption(f"🔁 Refreshed: {refreshed}")
