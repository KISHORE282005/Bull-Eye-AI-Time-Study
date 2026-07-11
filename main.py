import streamlit as st

pg = st.navigation([
    st.Page("app.py", title="App", icon="🏭", default=True),
    st.Page("pages/5_AI_Report.py", title="AI Report", icon="📊"),
])

pg.run()
