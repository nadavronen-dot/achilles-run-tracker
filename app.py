import os
import json
import streamlit as st
import streamlit.components.v1 as components

# Try to import garmin_sync
try:
    import garmin_sync
except ImportError:
    garmin_sync = None

st.set_page_config(
    page_title="מירוץ בוז'ולה 2026 - ניהול עומסים 8 ק״מ",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Streamlit
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
        background: #0f172a !important;
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
    .garmin-card {
        background: #1e293b;
        color: white;
        padding: 12px 18px;
        border-radius: 10px;
        margin: 10px 16px;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Garmin Connect Streamlit Integration Expander
if garmin_sync:
    saved_creds = garmin_sync.load_saved_credentials() or {}
    with st.expander("⌚ סנכרון ישיר מול שעון Garmin Connect (לחץ לפתיחה / סנכרון)"):
        col1, col2, col3 = st.columns([1.5, 1.5, 1])
        with col1:
            g_email = st.text_input("מייל Garmin Connect:", value=saved_creds.get("email", ""), key="g_email")
        with col2:
            g_pass = st.text_input("סיסמה:", value=saved_creds.get("password", ""), type="password", key="g_pass")
        with col3:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            sync_btn = st.button("🔄 סנכרן פעילות אחרונה", type="primary")

        if sync_btn:
            if not g_email or not g_pass:
                st.warning("אנא הזן מייל וסיסמה של חשבון Garmin Connect.")
            else:
                with st.spinner("מתחבר ל-Garmin Connect ושואב נתוני פעילות..."):
                    res = garmin_sync.fetch_latest_activity(g_email, g_pass)
                    if res.get("success"):
                        st.success(f"נמצאה פעילות: {res.get('activityName')} ({res.get('date')})")
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("מרחק", f"{res.get('distanceKm')} ק\"מ")
                        c2.metric("זמן", res.get("durationFormatted"))
                        c3.metric("קדנס ממוצע", f"{res.get('avgCadence') or '-'} SPM")
                        c4.metric("דופק ממוצע", f"{res.get('avgHr') or '-'} bpm")
                        
                        if res.get("cadenceFeedback"):
                            st.info(f"💡 דגש שיקום אכילס: {res.get('cadenceFeedback')}")
                    else:
                        st.error(res.get("error", "שגיאה בסנכרון מול גרמין"))

html_path = os.path.join(os.path.dirname(__file__), "index.html")
if not os.path.exists(html_path):
    html_path = "/Users/nadavronen/Documents/אישי/אימונים וספורט/מעקבים אישיים/achilles_training_app.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Render full interactive web app
components.html(html_content, height=1950, scrolling=True)

if __name__ == "__main__":
    from streamlit.web import cli as stcli
    import sys
    if not st.runtime.exists():
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())
