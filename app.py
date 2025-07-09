import streamlit as st
import openai
import os
import json
from dotenv import load_dotenv
from typing import List
import faiss
import numpy as np

load_dotenv()

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load FAISS index and document metadata
def load_faiss_index_and_metadata():
    index = faiss.read_index("vector_index/faiss.index")
    with open("vector_index/metadata.json", "r") as f:
        metadata = json.load(f)
    return index, metadata

# Embed the query
def embed_query(query: str) -> np.ndarray:
    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return np.array(response['data'][0]['embedding'], dtype=np.float32)

# Search the index
def search_index(query_embedding: np.ndarray, index, metadata, k: int = 5):
    D, I = index.search(np.array([query_embedding]), k)
    return [metadata[i] for i in I[0] if i < len(metadata)]

# Display results with deduplicated sources
def format_response(relevant_docs: List[dict], answer: str) -> str:
    response_parts = [answer.strip(), "\n\n**Sources:**"]

    # Deduplicate by source_url
    seen = set()
    unique_sources = []
    for doc in relevant_docs:
        url = doc["metadata"].get("source_url")
        if url and url not in seen:
            seen.add(url)
            unique_sources.append({
                "title": doc["metadata"].get("title", "Untitled"),
                "source_url": url
            })

    for i, src in enumerate(unique_sources):
        response_parts.append(f"{i + 1}. [{src['title']}]({src['source_url']})")

    return "\n".join(response_parts)

# Generate answer from GPT-4
def generate_answer(query: str, context: str) -> str:
    prompt = f"""
Answer the following question using the context below. Be concise and accurate.

Context:
{context}

Question: {query}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for answering questions about the U.S. Federal Reserve."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )
    return response["choices"][0]["message"]["content"]

# Streamlit app
st.set_page_config(page_title="FedBot: About the Fed Q/A")
st.title("FedBot")
st.subheader("Ask questions about the Federal Reserve")

query = st.text_input("Enter your question")

if query:
    with st.spinner("Searching..."):
        index, metadata = load_faiss_index_and_metadata()
        query_embedding = embed_query(query)
        relevant_docs = search_index(query_embedding, index, metadata, k=5)

        context = "\n\n".join(doc["text"] for doc in relevant_docs)
        answer = generate_answer(query, context)
        final_response = format_response(relevant_docs, answer)

        st.markdown(final_response, unsafe_allow_html=True)
