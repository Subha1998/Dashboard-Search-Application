import streamlit as st

def render_dashboard_cards(df):
    st.markdown("## 🗂️ Dashboards")
    for i in range(0, len(df), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(df):
                row = df.iloc[i + j]
                with col:
                    # Inline style now includes uniform vertical margin
                    col.markdown(f'''
                        <div class="dashboard-card" style="
                            border:1px solid #e0e0e0;
                            border-radius:12px;
                            padding:16px;
                            background:#fff;
                            box-shadow:0 2px 8px rgba(0,0,0,0.05);
                            height:100%;
                            display:flex;
                            flex-direction:column;
                            justify-content:space-between;
                            margin:20px 0;">
                            <img src="{row['Thumbnail URL']}" style="
                                width:100%;
                                height:160px;
                                object-fit:cover;
                                border-radius:8px;
                                margin-bottom:12px;" />
                            <div style="font-size:1.1rem; font-weight:600; margin-bottom:6px;">
                                🧾 {row['Dashboard Name']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Tab:</b> {row['Tab Name']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>View:</b> {row['View Name']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>KPI:</b> {row['Primary KPI']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Owner:</b> {row['Owner']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Business Unit:</b> {row['Business Unit']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Region:</b> {row['Region']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Last Updated:</b> {row['Last Updated']}
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:4px;">
                                <b>Tags:</b> <i>{row['Tags']}</i>
                            </div>
                            <div style="font-size:0.9rem; margin-bottom:12px;">
                                <i>{row['Description']}</i>
                            </div>
                            <a href="{row['Dashboard Link']}" target="_blank" style="
                                margin-top:auto;
                                font-size:0.9rem;
                                color:#0066cc;">
                                🔗 Open Dashboard
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
