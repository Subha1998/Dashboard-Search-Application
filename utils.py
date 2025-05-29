import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer
import os

CSV_PATH = "Richer_Enhanced_Dashboard_Metadata_With_Thumbnails.csv"
PENDING_PATH = "pending_submissions.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df["search_text"] = df.apply(
        lambda x: (
            f"{x['Dashboard Name']} {x['Tab Name']} "
            f"{x['View Name']} {x['Description']} "
            f"{x['Tags']} {x['Owner']} {x['Primary KPI']} "
            f"{x['Business Unit']} {x['Region']}"
        ),
        axis=1
    )
    return df

@st.cache_resource
def load_model_and_embeddings(df):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(df["search_text"].tolist(), show_progress_bar=True)
    return model, embeddings

def save_dashboard(data):
    df = pd.read_csv(CSV_PATH)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def delete_dashboard(dashboard_name):
    df = pd.read_csv(CSV_PATH)
    df = df[df["Dashboard Name"] != dashboard_name]
    df.to_csv(CSV_PATH, index=False)

def save_pending_submission(data: dict):
    """Append a new dashboard entry to the pending_submissions.csv."""
    if os.path.exists(PENDING_PATH):
        df = pd.read_csv(PENDING_PATH)
    else:
        df = pd.DataFrame()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(PENDING_PATH, index=False)
