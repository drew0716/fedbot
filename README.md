# FedBot: About the Fed Q\&A

**FedBot** is an interactive question-and-answer web app that uses Retrieval-Augmented Generation (RAG) to help users explore official information about the United States Federal Reserve. It focuses exclusively on content from the **"About the Fed"** section of [federalreserve.gov](https://www.federalreserve.gov/aboutthefed.htm).

FedBot uses a semantic search pipeline with document embedding, vector indexing, and large language model responses from Anthropic’s Claude 3.

---

## 🔎 Features

* Natural language question interface
* Automatic weekly crawl + chunk + reindex pipeline
* FAISS-powered vector search over Federal Reserve documents
* Context-aware answers using Claude 3 (via API)
* Source links for transparency
* Last updated timestamp shown in-app

---

## 🚀 Try the App

🔺 **[Launch FedBot](https://fedbot.streamlit.app)**

> **Note:** Access to the hosted version is currently limited.
> Contact [Drew](mailto:drew0716@gmail.com) to request access.

---

## ⚙️ Tech Stack

* **Streamlit** – Interactive web UI
* **BeautifulSoup** – Web crawling & parsing
* **FAISS** – Semantic vector index for fast document similarity search
* **Sentence Transformers** – Embedding model (`all-MiniLM-L6-v2`)
* **Anthropic Claude 3** – Large language model API for natural answers
* **GitHub Actions** – Automated weekly refresh of indexed content
* **Python** – Scripting & orchestration

---

## 🔁 Automatic Refresh (Every Other Day)

FedBot is automatically kept up-to-date using a GitHub Actions workflow that runs every other day. It performs the following:

1. Crawls the latest “About the Fed” pages
2. Extracts and chunks the content
3. Rebuilds the vector index
4. Updates `last_updated.txt` and `force_redeploy.txt`
5. Commits changes to GitHub, triggering a Streamlit redeploy

You can also manually trigger the refresh via the GitHub **Actions tab**.

---

## 📁 Project Structure

```
fedbot/
├── .github/workflows/update_index.yml   # GitHub Action for automation
├── .streamlit/config.toml               # Streamlit config
├── app.py                               # Streamlit app interface
├── crawl_about_fed.py                   # Crawls the Fed website
├── extract_and_chunk.py                 # Splits documents into chunks
├── embed_and_store.py                   # Embeds chunks and builds FAISS index
├── ingest_documents.py                  # Optional ingestion utility
├── chunks/                              # Text chunks used for indexing
├── about_the_fed_pages/                 # Raw crawled pages (optional to commit)
├── chunk_data.pkl                       # Chunk metadata
├── faiss_index.index                    # Vector index for semantic search
├── metadata.pkl                         # Chunk-to-source metadata
├── last_updated.txt                     # Timestamp of last refresh
├── force_redeploy.txt                   # Triggers Streamlit redeploy
├── requirements.txt                     # Python dependencies
├── .gitignore
├── .env                                 # Local API keys (not committed)
└── README.md
```

---

## 🔐 API Keys

To run the app locally, create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Ensure `.env` is in `.gitignore` to avoid exposing credentials.

---

## ✅ Run Locally

1. Clone the repo
2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Add your `.env` with your API key
5. Launch the app:

   ```bash
   streamlit run app.py
   ```

---

## 📩 Questions?

For access or support, reach out to [Drew](mailto:drew0716@gmail.com).

---

## 🤝 License

This project is for educational and informational purposes only.
It is **not affiliated with or endorsed by the Federal Reserve System**.

---
