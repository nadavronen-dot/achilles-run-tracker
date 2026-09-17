import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="מירוץ בוז'ולה 2026 - ניהול עומסים 8 ק״מ",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu, header, footer {
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
        background: #f8fafc !important;
    }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    iframe {
        width: 100% !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

html_path = os.path.join(os.path.dirname(__file__), "index.html")
if not os.path.exists(html_path):
    html_path = "/Users/nadavronen/Documents/אישי/אימונים וספורט/מעקבים אישיים/achilles_training_app.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=1850, scrolling=True)

if __name__ == "__main__":
    from streamlit.web import cli as stcli
    import sys
    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
