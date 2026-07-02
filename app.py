import streamlit as st
import feedparser
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from groq import Groq

st.set_page_config(page_title="World Cup Buzz", page_icon="⚽", layout="centered")

# ---------- CONFIG ----------
FEEDS = {
    "BBC Football": "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "ESPN Soccer": "https://www.espn.com/espn/rss/soccer/news",
    "Guardian Football": "https://www.theguardian.com/football/rss",
}

WORLDCUP_KEYWORDS = ["world cup", "fifa", "round of", "knockout", "group stage"]

PERSONAS = {
    "Excited Match Commentator": "an excited, over-the-top match commentator",
    "Deadpan Tactics Analyst": "a deadpan tactics analyst who finds everything mildly underwhelming",
    "Classic British Pundit": "a classic British football pundit doing a fiery halftime rant",
}

# ---------- CACHED RESOURCES ----------
@st.cache_resource
def load_embed_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_groq_client():
    api_key = st.secrets["GROQ_API_KEY"]
    return Groq(api_key=api_key)

# ---------- DATA PIPELINE ----------
@st.cache_data(ttl=900)  # refresh feed data every 15 minutes
def fetch_worldcup_articles():
    all_articles = []
    for source, feed_url in FEEDS.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:25]:
            all_articles.append({
                "source": source,
                "title": entry.title,
                "summary": entry.get("summary", ""),
                "link": entry.link,
                "published": entry.get("published", ""),
            })

    worldcup_articles = [
        a for a in all_articles
        if any(kw in (a["title"] + a["summary"]).lower() for kw in WORLDCUP_KEYWORDS)
    ]
    return worldcup_articles


def build_documents(articles):
    documents = []
    for article in articles:
        text = f"{article['title']}. {article['summary']}"
        documents.append({
            "text": text,
            "source": article["source"],
            "title": article["title"],
            "link": article["link"],
            "published": article["published"],
        })
    return documents


def build_index(embed_model, documents):
    texts = [doc["text"] for doc in documents]
    embeddings = embed_model.encode(texts)
    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)
    return index


def retrieve_relevant_articles(query, embed_model, index, documents, top_k=5):
    query_embedding = embed_model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    return [documents[idx] for idx in indices[0]]


def ask_world_cup_buzz(question, persona_desc, client, embed_model, index, documents, top_k=5):
    relevant_docs = retrieve_relevant_articles(question, embed_model, index, documents, top_k=top_k)

    context = "\n\n".join([
        f"[{doc['source']}] {doc['text']} (Published: {doc['published']})"
        for doc in relevant_docs
    ])

    system_prompt = f"""You are "World Cup Buzz," a football news assistant with the personality of {persona_desc}.
Answer the user's question using ONLY the information in the provided articles below.
Stay fully in character - be entertaining, but don't make up facts not in the articles.
If the articles don't contain enough info to answer, say so in character.
Always mention which source(s) your info came from.

ARTICLES:
{context}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content, relevant_docs


# ---------- UI ----------
st.title("⚽ World Cup Buzz")
st.caption("A RAG-powered World Cup news assistant — live headlines, your choice of persona, source-grounded answers.")

with st.sidebar:
    st.header("Settings")
    persona_label = st.selectbox("Choose a persona", list(PERSONAS.keys()))
    top_k = st.slider("Articles to retrieve per question", 3, 10, 5)
    if st.button("🔄 Refresh news feed"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

# Load everything
with st.spinner("Loading latest World Cup news..."):
    embed_model = load_embed_model()
    client = load_groq_client()
    articles = fetch_worldcup_articles()
    documents = build_documents(articles)

    if not documents:
        st.error("No World Cup articles found right now. Try refreshing in a few minutes.")
        st.stop()

    index = build_index(embed_model, documents)

st.success(f"Loaded {len(documents)} live World Cup articles from {len(FEEDS)} sources.")

question = st.text_input("Ask about the World Cup:", placeholder="e.g. What happened in today's Round of 32 matches?")

if st.button("Get the Buzz", type="primary") and question:
    with st.spinner("Digging through the latest headlines..."):
        answer, sources = ask_world_cup_buzz(
            question, PERSONAS[persona_label], client, embed_model, index, documents, top_k=top_k
        )
    st.markdown("### 📣 The Buzz")
    st.write(answer)

    with st.expander("📰 Sources used"):
        for s in sources:
            st.markdown(f"- [{s['title']}]({s['link']}) — *{s['source']}*, {s['published']}")

st.divider()
st.caption("Built with Streamlit, sentence-transformers, FAISS, and Groq (Llama 3.3 70B). News refreshes every 15 minutes.")
