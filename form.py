import streamlit as st
from utils import load_data, save_pending_submission
import datetime

ADMIN_PASSWORD = "iamadmin"  # Replace with your actual admin password

def show_add_dashboard_form():
    st.subheader("🔒 Admin Access Required to Submit Dashboard")

    # — Admin login state —
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        pw = st.text_input("Enter Admin Password", type="password", key="admin_pw")
        if pw == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.success("✅ Authentication successful!")
        else:
            if pw:
                st.error("❌ Incorrect password")
            return

    st.subheader("➕ Submit New Dashboard for Approval")

    # — Form state helpers —
    if "form_submitted" not in st.session_state:
        st.session_state.form_submitted = False
    if "prevent_repeat" not in st.session_state:
        st.session_state.prevent_repeat = False

    # Prevent duplicates against the *approved* set
    existing = load_data()["Dashboard Name"].dropna().str.lower().tolist()

    # Keep inputs across errors
    fields = [
        "Dashboard Name", "Tab Name", "View Name", "Description",
        "Tags", "Owner", "Primary KPI", "Business Unit",
        "Region", "Dashboard Link", "Thumbnail URL"
    ]
    for f in fields:
        key = f"input_{f}"
        if key not in st.session_state or st.session_state.form_submitted:
            st.session_state[key] = ""
    if "input_Last Updated" not in st.session_state or st.session_state.form_submitted:
        st.session_state["input_Last Updated"] = datetime.date.today()

    # — The Form —
    with st.form("pending_dashboard_form", clear_on_submit=False):
        entry = {
            "Dashboard Name": st.text_input(
                "Dashboard Name *",
                value=st.session_state["input_Dashboard Name"]
            ),
            "Tab Name": st.text_input(
                "Tab Name *",
                value=st.session_state["input_Tab Name"]
            ),
            "View Name": st.text_input(
                "View Name *",
                value=st.session_state["input_View Name"]
            ),
            "Description": st.text_area(
                "Description *",
                value=st.session_state["input_Description"]
            ),
            "Tags": st.text_input(
                "Tags (comma separated) *",
                value=st.session_state["input_Tags"]
            ),
            "Owner": st.text_input(
                "Owner *",
                value=st.session_state["input_Owner"]
            ),
            "Primary KPI": st.text_input(
                "Primary KPI *",
                value=st.session_state["input_Primary KPI"]
            ),
            "Business Unit": st.text_input(
                "Business Unit *",
                value=st.session_state["input_Business Unit"]
            ),
            "Region": st.text_input(
                "Region *",
                value=st.session_state["input_Region"]
            ),
            "Last Updated": st.date_input(
                "Last Updated *",
                value=st.session_state["input_Last Updated"]
            ),
            "Dashboard Link": st.text_input(
                "Dashboard Link (URL) *",
                value=st.session_state["input_Dashboard Link"]
            ),
            "Thumbnail URL": st.text_input(
                "Thumbnail URL (image link) *",
                value=st.session_state["input_Thumbnail URL"]
            )
        }

        # Preview via URL
        if entry["Thumbnail URL"]:
            try:
                st.image(entry["Thumbnail URL"], use_column_width=True)
            except:
                st.warning(f"⚠️ Could not load image from URL: {entry['Thumbnail URL']}")

        submitted = st.form_submit_button("Submit for Approval")

        if submitted and not st.session_state.prevent_repeat:
            # Validate required fields
            missing = [k for k, v in entry.items() if not v]
            if missing:
                st.error(f"Please fill all required fields: {', '.join(missing)}")
                for k, v in entry.items():
                    st.session_state[f"input_{k}"] = v

            elif entry["Dashboard Name"].strip().lower() in existing:
                st.error("❌ A dashboard with this name already exists in approved set.")
                for k, v in entry.items():
                    st.session_state[f"input_{k}"] = v

            else:
                # Save to pending queue
                save_pending_submission(entry)
                st.toast("📨 Dashboard submitted and pending approval", icon="✉️")
                st.session_state.form_submitted = True
                st.session_state.prevent_repeat = True

                # Clear session inputs
                for f in fields:
                    st.session_state[f"input_{f}"] = ""
                st.session_state["input_Last Updated"] = datetime.date.today()
                st.experimental_rerun()
