# ⚽ World Cup Buzz

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://world-cup-buzz.streamlit.app)

A RAG-powered FIFA World Cup 2026 news assistant built with free, open-source tools.

## How it works
1. Pulls live World Cup headlines every 15 mins from BBC, ESPN & Guardian RSS feeds
2. Embeds articles locally using `sentence-transformers` (all-MiniLM-L6-v2)
3. Stores vectors in FAISS for fast semantic retrieval
4. Retrieves top relevant articles per question
5. Passes context + chosen persona to Groq's Llama 3.3 70B
6. Returns grounded, cited, personality-driven answers

## Tech Stack
| Layer | Technology |
|---|---|
| LLM | Groq API (Llama 3.3 70B) |
| Embeddings | sentence-transformers (local, free) |
| Vector Store | FAISS |
| Data Source | RSS feeds (BBC, ESPN, Guardian) |
| UI | Streamlit |
| Deployment | Google Cloud Run + Docker |

## Run locally
```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
streamlit run app.py
```
