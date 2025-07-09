import os
import pickle
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
import anthropic

# Anthropic API key
api_key = st.secrets["ANTHROPIC_API_KEY"]
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
    index = faiss.read_index("faiss_index.index")
    with open("metadata.pkl", "rb") as f:
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
    D, I = index.search(q_embedding, k=10)

    context = ""
    sources = []
    added = 0

    for i in I[0]:
        meta = metadata[i]
        if meta["type"] != "aboutthefed":
            continue

        filepath = os.path.join("chunks", meta["filename"])
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        context += f"\n---\n{content}"

        title_raw = meta.get("source", "Unknown Source")
        title_parts = title_raw.replace(".txt", "").replace("_chunk", "").replace("_", " ").split()
        if "fedexplained" in title_parts:
            try:
                section_index = title_parts.index("fedexplained") + 1
                title = f"About the Fed: Fed Explained – {' '.join(title_parts[section_index:]).title()}"
            except:
                title = "About the Fed: Fed Explained"
        else:
            title = f"About the Fed: {' '.join(title_parts).title()}"

        sources.append((title, meta.get("url")))
        added += 1
        if added >= 5:
            break

    if not context:
        st.warning("No relevant 'About the Fed' content found for your question.")
    else:
        system_prompt = "You are a helpful assistant answering questions using verified information from the Federal Reserve's public About the Fed pages."
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
  This tool uses public data from federalreserve.gov and Anthropic's Claude 3 model to provide answers based on "About the Fed" content.<br>
  <strong>Disclaimer:</strong> This tool is not affiliated with or endorsed by the Federal Reserve System.
</footer>
""", unsafe_allow_html=True)

# 🔁 Show force redeploy timestamp (optional but useful)
if os.path.exists("force_redeploy.txt"):
    with open("force_redeploy.txt", "r") as f:
        refreshed = f.read().strip()
    st.caption(f"🔁 Refreshed: {refreshed}")