import streamlit as st
import pandas as pd
import os
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

st.set_page_config(page_title="Dashboard Search Assistant", layout="wide")
warnings.filterwarnings("ignore")
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# -------- Load Data --------
@st.cache_data
def load_data():
    df = pd.read_csv("Richer_Enhanced_Dashboard_Metadata_With_Thumbnails.csv")
    df["search_text"] = df.apply(
        lambda x: f"{x['Dashboard Name']} {x['Tab Name']} {x['View Name']} {x['Description']} "
                  f"{x['Tags']} {x['Owner']} {x['Primary KPI']} {x['Business Unit']} {x['Region']}",
        axis=1
    )
    return df

# -------- Load Embeddings --------
@st.cache_resource
def load_model_and_embeddings(data):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(data["search_text"].tolist(), show_progress_bar=True)
    return model, embeddings

# -------- Fuzzy Score --------
def fuzzy_score(query, text):
    return fuzz.partial_ratio(query.lower(), text.lower()) / 100

# -------- Load Data & Model --------
df = load_data()
model, vectors = load_model_and_embeddings(df)

# -------- CSS Styling --------
st.markdown("""
    <style>
    .dashboard-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        background-color: #ffffff;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .dashboard-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .dashboard-img {
        width: 100%;
        height: 160px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .dashboard-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .dashboard-meta {
        font-size: 0.9rem;
        margin-bottom: 4px;
    }
    .dashboard-link {
        margin-top: auto;
        font-size: 0.9rem;
        color: #0066cc;
    }
    .stTextInput > div > input {
        font-size: 16px;
        padding: 10px;
    }
    .stButton > button {
        background-color: #eeeeee;
        color: #333;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px 16px;
    }
    </style>
""", unsafe_allow_html=True)

# -------- App Title --------
st.markdown("## 📊 Dashboard Search Assistant")

# -------- Session Init --------
if "query" not in st.session_state:
    st.session_state.query = ""

# -------- Inline Clear + Search Input --------
col1, col2 = st.columns([9, 1])

with col2:
    clear_clicked = False
    if st.session_state.query:
        clear_clicked = st.button("✖", help="Clear search")

if clear_clicked:
    st.session_state.query = ""
    st.experimental_rerun()

with col1:
    st.text_input("Search dashboards", key="query", placeholder="e.g. Sales Q4 revenue performance")

query = st.session_state.query

# -------- Search Logic --------
if query:
    query_vec = model.encode([query])
    cosine_scores = cosine_similarity(query_vec, vectors)[0]

    results = []
    for i, row in df.iterrows():
        sem_score = cosine_scores[i]
        fuzzy_fields = f"{row['Dashboard Name']} {row['Tab Name']} {row['View Name']} {row['Description']}"
        fuz_score = fuzzy_score(query, fuzzy_fields)
        final_score = 0.6 * sem_score + 0.4 * fuz_score
        results.append((final_score, i))

    top_matches = sorted(results, key=lambda x: x[0], reverse=True)[:3]
    df = df.iloc[[idx for _, idx in top_matches]]

# -------- Display Dashboard Cards --------
st.markdown("## 🗂️ Dashboards")

for i in range(0, len(df), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(df):
            row = df.iloc[i + j]
            with col:
                col.markdown(f"""
                <div class="dashboard-card">
                    <img src="{row['Thumbnail URL']}" class="dashboard-img" />
                    <div class="dashboard-title">🧾 {row['Dashboard Name']}</div>
                    <div class="dashboard-meta"><b>Tab:</b> {row['Tab Name']}</div>
                    <div class="dashboard-meta"><b>View:</b> {row['View Name']}</div>
                    <div class="dashboard-meta"><b>KPI:</b> {row['Primary KPI']}</div>
                    <div class="dashboard-meta"><b>Owner:</b> {row['Owner']}</div>
                    <div class="dashboard-meta"><b>Business Unit:</b> {row['Business Unit']}</div>
                    <div class="dashboard-meta"><b>Region:</b> {row['Region']}</div>
                    <div class="dashboard-meta"><b>Last Updated:</b> {row['Last Updated']}</div>
                    <div class="dashboard-meta"><b>Tags:</b> <i>{row['Tags']}</i></div>
                    <div class="dashboard-meta"><i>{row['Description']}</i></div>
                    <a class="dashboard-link" href="{row['Dashboard Link']}" target="_blank">🔗 Open Dashboard</a>
                </div>
                """, unsafe_allow_html=True)