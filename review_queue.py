import streamlit as st
import pandas as pd
import os

PENDING_FILE = "pending_submissions.csv"
MAIN_FILE    = "Richer_Enhanced_Dashboard_Metadata_With_Thumbnails.csv"

def load_pending():
    return pd.read_csv(PENDING_FILE) if os.path.exists(PENDING_FILE) else pd.DataFrame()

def load_main():
    return pd.read_csv(MAIN_FILE) if os.path.exists(MAIN_FILE) else pd.DataFrame()

def save_pending(df):
    df.to_csv(PENDING_FILE, index=False)

def append_to_main(dashboard: pd.Series):
    df_main = load_main()
    df_main = pd.concat([df_main, pd.DataFrame([dashboard])], ignore_index=True)
    df_main.to_csv(MAIN_FILE, index=False)

def show_approval_queue():
    st.subheader("📝 Pending Dashboard Approvals")
    df = load_pending()
    if df.empty:
        st.info("No pending dashboards to review.")
        return

    for i, row in df.iterrows():
        with st.expander(f"📋 {row['Dashboard Name']} ({row['Owner']})"):
            # show all fields
            for col in df.columns:
                st.markdown(f"**{col}:** {row[col]}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve", key=f"approve_{i}"):
                    append_to_main(row)
                    df = df.drop(i)
                    save_pending(df)
                    st.success("Dashboard approved and added to main dataset.")
                    st.experimental_rerun()
            with col2:
                if st.button("❌ Reject", key=f"reject_{i}"):
                    df = df.drop(i)
                    save_pending(df)
                    st.warning("Dashboard rejected and removed from pending list.")
                    st.experimental_rerun()