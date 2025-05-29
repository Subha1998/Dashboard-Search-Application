import streamlit as st

def sidebar():
    st.sidebar.title("Navigation")
    return st.sidebar.radio(
        "Go to",
        [
            "Show Dashboards",
            "Add Dashboard",
            "Review Submissions",
            "Delete Dashboard"
        ],
    )
