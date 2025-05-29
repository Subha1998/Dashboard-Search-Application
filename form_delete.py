import streamlit as st
from utils import load_data, delete_dashboard
import pandas as pd

ADMIN_PASSWORD = "iamadmin"  # Replace with your actual password

def show_delete_dashboard_form():
    st.subheader("🗑️ Delete Dashboard (Admin Only)")

    # Step 1: Authenticate admin
    if "admin_delete_authenticated" not in st.session_state:
        st.session_state.admin_delete_authenticated = False

    if not st.session_state.admin_delete_authenticated:
        password = st.text_input("Enter Admin Password", type="password", key="admin_pw_del")
        if password == ADMIN_PASSWORD:
            st.session_state.admin_delete_authenticated = True
            st.success("✅ Authentication successful!")
        else:
            if password != "":
                st.error("❌ Incorrect password")
            return

    # Step 2: Load and display dashboard names
    df = load_data()
    dashboard_names = df["Dashboard Name"].dropna().unique().tolist()

    if not dashboard_names:
        st.warning("⚠️ No dashboards available to delete.")
        return

    selected_dashboard = st.selectbox("Select Dashboard to Delete", dashboard_names, key="delete_select")

    # Step 3: Confirmation logic
    if selected_dashboard:
        if "confirm_delete_trigger" not in st.session_state:
            st.session_state.confirm_delete_trigger = False

        if st.button("🗑️ Delete Selected Dashboard"):
            st.session_state.confirm_delete_trigger = True

        if st.session_state.confirm_delete_trigger:
            st.warning(f"Are you sure you want to delete '{selected_dashboard}'?")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Yes, Delete", key="yes_delete"):
                    delete_dashboard(selected_dashboard)
                    st.success(f"✅ Dashboard '{selected_dashboard}' deleted successfully!")
                    st.session_state.confirm_delete_trigger = False
                    st.cache_data.clear()
                    st.experimental_rerun()
            with col2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    st.session_state.confirm_delete_trigger = False