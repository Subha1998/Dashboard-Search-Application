import streamlit as st
st.set_page_config(page_title="Dashboard Search Assistant", layout="wide")

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import os

# Optional: Mac-specific fix for torch Metal issues
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# -------- Load Data --------
@st.cache_data
def load_data():
    df = pd.read_csv("Enhanced_Dashboard_Metadata.csv")
    df["search_text"] = df.apply(
        lambda x: f"{x['Dashboard Name']} {x['Tab Name']} {x['View Name']} {x['Description']} {x['Tags']} {x['Owner']} {x['Primary KPI']}", axis=1
    )
    return df

# -------- Load Embeddings --------
@st.cache_resource
def load_model_and_embeddings(data):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(data["search_text"].tolist(), show_progress_bar=True)
    return model, embeddings

# -------- Fuzzy Match Helper --------
def fuzzy_score(query, text):
    return fuzz.partial_ratio(query.lower(), text.lower())

# -------- Load & Prep --------
df = load_data()
model, vectors = load_model_and_embeddings(df)

# -------- UI --------
st.title("📊 Dashboard Search Assistant")
query = st.text_input("Ask me anything about your dashboards:")

if query:
    query_vec = model.encode([query])
    cosine_scores = cosine_similarity(query_vec, vectors)[0]

    results = []
    for i, row in df.iterrows():
        sem_score = cosine_scores[i]

        fuzzy_fields = f"{row['Dashboard Name']} {row['Tab Name']} {row['View Name']} {row['Description']}"
        fuz_score = fuzzy_score(query, fuzzy_fields) / 100  # Normalize to 0–1

        # Weighted combination (tweak ratio if needed)
        final_score = 0.6 * sem_score + 0.4 * fuz_score

        results.append((final_score, i))

    top_matches = sorted(results, key=lambda x: x[0], reverse=True)[:3]

    st.subheader("🔍 Top Matches")
    for score, idx in top_matches:
        row = df.iloc[idx]
        st.markdown(f"### 🧾 {row['Dashboard Name']}")
        st.markdown(f"**Tab:** {row['Tab Name']}  \n**View:** {row['View Name']}")
        st.markdown(f"**Primary KPI:** {row['Primary KPI']}  \n**Owner:** {row['Owner']}  \n**Last Updated:** {row['Last Updated']}")
        st.markdown(f"**Tags:** {row['Tags']}")
        st.markdown(f"🔗 [Open Dashboard]({row['Dashboard Link']})", unsafe_allow_html=True)
        st.markdown(f"📄 _{row['Description']}_")
        st.markdown("---")