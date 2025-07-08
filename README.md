# FedBot: About the Fed Q&A

**FedBot** is an interactive question-and-answer web application that uses Retrieval-Augmented Generation (RAG) to help users explore information about the United States Federal Reserve. This app focuses exclusively on content found in the **"About the Fed"** section of [federalreserve.gov](https://www.federalreserve.gov/aboutthefed.htm).

Built with Python, FAISS, Sentence Transformers, and Streamlit, FedBot combines web crawling, text chunking, semantic search, and large language model responses to provide helpful and relevant answers based on official sources.

---

## 🔎 Features

- Natural language question interface
- Embedded search powered by FAISS and Sentence Transformers
- Answers generated using Anthropic’s Claude 3 model (via API)
- Only uses content from the public "About the Fed" section of federalreserve.gov
- Source links shown for transparency and traceability

---

## 🌐 Try the App

▶️ [**Launch FedBot**](https://fedbot.streamlit.app)

> **Note**: Access to the hosted version is currently limited.  
> If you'd like to test or use FedBot, please [contact Drew](mailto:drew0716@gmail.com) to request access.

---

## ⚙️ Tech Stack

- **Streamlit** – UI and frontend
- **BeautifulSoup** – Web crawling and HTML parsing
- **FAISS** – Semantic vector index for search
- **SentenceTransformers** – Text embeddings (`all-MiniLM-L6-v2`)
- **Anthropic Claude 3 API** – Large language model for answers
- **Python** – Glue code and preprocessing

---

## 📁 Project Structure

```
fedbot/
├── app.py                  # Streamlit frontend
├── crawl_about_fed.py      # Web crawler for "About the Fed"
├── extract_and_chunk.py    # Chunking raw text
├── embed_and_store.py      # Embedding and FAISS indexing
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed to Git)
├── .gitignore
├── README.md
└── ...
```

---

## 🔐 API Keys

To run locally, set your Anthropic Claude API key in a `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Make sure `.env` is listed in your `.gitignore` to prevent accidental commits.

---

## 🤝 License

This project is for educational and informational purposes only.  
It is **not affiliated with or endorsed by the Federal Reserve System**.

---
