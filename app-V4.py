import streamlit as st
from sidebar import sidebar
from cards import render_dashboard_cards
from form import show_add_dashboard_form
from form_delete import show_delete_dashboard_form
from review_queue import show_approval_queue
from utils import load_data, load_model_and_embeddings

# — PAGE CONFIG & STYLING —
st.set_page_config(page_title="Dashboard Search Assistant", layout="wide")

# (Optional) Inject any global CSS here
st.markdown("""
    <style>
    /* Ensure uniform vertical spacing of cards */
    .dashboard-card {
        margin: 20px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Dashboard Search Assistant")

# — SIDEBAR NAVIGATION —
choice = sidebar()

# — LOAD DATA & MODEL ONCE —
df = load_data()
model, vectors = load_model_and_embeddings(df)

# — COMMON SEARCH HELPERS —
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

def fuzzy_score(q, text):
    return fuzz.partial_ratio(q.lower(), text.lower()) / 100

# — “Show Dashboards” (search + list) —
if choice == "Show Dashboards":
    # initialize query state
    if "query" not in st.session_state:
        st.session_state.query = ""
    # render search input
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.session_state.query and st.button("✖", help="Clear search"):
            st.session_state.query = ""
            st.experimental_rerun()
    with col1:
        st.text_input("Search dashboards", key="query", placeholder="e.g. Sales Q4 revenue performance")
    query = st.session_state.query

    # if user typed something, filter; otherwise show all
    if query:
        q_vec = model.encode([query])
        scores = cosine_similarity(q_vec, vectors)[0]
        results = []
        for i, row in df.iterrows():
            sem = scores[i]
            fuz = fuzzy_score(query, f"{row['Dashboard Name']} {row['Tab Name']} {row['View Name']} {row['Description']}")
            results.append((0.6 * sem + 0.4 * fuz, i))
        top = sorted(results, key=lambda x: x[0], reverse=True)[:1]
        df_to_show = df.iloc[[idx for _, idx in top]]
    else:
        df_to_show = df

    render_dashboard_cards(df_to_show)

# — “Add Dashboard” —
elif choice == "Add Dashboard":
    show_add_dashboard_form()

# — “Review Submissions” —
elif choice == "Review Submissions":
    show_approval_queue()

# — “Delete Dashboard” —
elif choice == "Delete Dashboard":
    show_delete_dashboard_form()
