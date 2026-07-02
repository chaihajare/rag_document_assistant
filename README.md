# ⚽ World Cup Buzz

A RAG-powered World Cup 2026 news assistant built with:
- **Groq** (Llama 3.3 70B) — LLM for persona-driven answers
- **sentence-transformers** — local embeddings (all-MiniLM-L6-v2)
- **FAISS** — vector similarity search
- **feedparser** — live RSS news ingestion (BBC, ESPN, Guardian)
- **Streamlit** — interactive UI

## How it works
1. Pulls live World Cup headlines from 3 RSS feeds every 15 minutes
2. Embeds each article using a local sentence-transformer model
3. On each question, retrieves the most semantically relevant articles via FAISS
4. Passes retrieved context + chosen persona to Groq's Llama 3.3 70B
5. Returns a grounded, cited, personality-driven answer

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Set `GROQ_API_KEY` as an environment variable or secret before deploying.
