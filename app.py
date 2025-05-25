import streamlit as st
st.set_page_config(page_title="Dashboard Search Assistant", layout="wide")

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Optional: Torch fix for macOS Metal backend issues
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("Enhanced_Dashboard_Metadata.csv")
    df["search_text"] = df.apply(
        lambda x: f"{x['Dashboard Name']} {x['Tab Name']} {x['View Name']} {x['Description']} {x['Tags']} {x['Owner']} {x['Primary KPI']}", axis=1
    )
    return df

# Load embedding model and compute vectors (cached)
@st.cache_resource
def load_model_and_embeddings(data):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(data["search_text"].tolist(), show_progress_bar=True)
    return model, embeddings

# Load data and model
df = load_data()
model, vectors = load_model_and_embeddings(df)

# UI Input
st.title("📊 Dashboard Search Assistant")
query = st.text_input("Ask me anything about your dashboards:")

if query:
    query_vec = model.encode([query])
    scores = cosine_similarity(query_vec, vectors)[0]
    top_indices = scores.argsort()[-3:][::-1]

    st.subheader("🔍 Top Matches")
    for idx in top_indices:
        row = df.iloc[idx]
        st.markdown(f"### 🧾 {row['Dashboard Name']}")
        st.markdown(f"**Tab:** {row['Tab Name']}  \n**View:** {row['View Name']}")
        st.markdown(f"**Primary KPI:** {row['Primary KPI']}  \n**Owner:** {row['Owner']}  \n**Last Updated:** {row['Last Updated']}")
        st.markdown(f"**Tags:** {row['Tags']}")
        st.markdown(f"🔗 [Open Dashboard]({row['Dashboard Link']})", unsafe_allow_html=True)
        st.markdown(f"📄 _{row['Description']}_")
        st.markdown("---")