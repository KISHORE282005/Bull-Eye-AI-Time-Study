import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

from utils.loader import TimeStudyLoader

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------

st.set_page_config(
    page_title="Lean Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Lean Manufacturing Analysis")
st.caption("AI Generated Lean Waste Analysis")
st.divider()

# ---------------------------------------------------
# Load JSON
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_FILE = BASE_DIR / "output" / "time_study.json"

loader = TimeStudyLoader(JSON_FILE)
loader.load()

data = loader.get_json()
overall = loader.get_overall()
df = loader.get_activity_dataframe()

# ---------------------------------------------------
# KPI
# ---------------------------------------------------

va = overall["estimated_value_added_time"]
nva = overall["estimated_non_value_added_time"]
walking = overall["walking_time"]
idle = overall["operator_idle_time"]
cycle = overall["cycle_time_seconds"]

total = max(va + nva, 1)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Cycle Time", f"{cycle} sec")
col2.metric("VA Time", f"{va} sec")
col3.metric("NVA Time", f"{nva} sec")
col4.metric("Walking", f"{walking} sec")

st.divider()

# ---------------------------------------------------
# VA vs NVA
# ---------------------------------------------------

fig = px.pie(
    names=["Value Added","Non Value Added"],
    values=[va,nva],
    hole=0.5,
    title="VA vs NVA"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---------------------------------------------------
# Value Added Table
# ---------------------------------------------------

st.subheader("Value Added Activities")

va_df = df[df["value_added"]=="Yes"]

st.dataframe(
    va_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------
# Non Value Added
# ---------------------------------------------------

st.subheader("Non Value Added Activities")

nva_df = df[df["value_added"]=="No"]

st.dataframe(
    nva_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------
# Lean Observations
# ---------------------------------------------------

st.subheader("Lean Observations")

for item in data["lean_observations"]:

    st.warning(item)

st.divider()

# ---------------------------------------------------
# Opportunities
# ---------------------------------------------------

st.subheader("Improvement Opportunities")

for item in data["productivity_opportunities"]:

    st.success(item)

st.divider()

# ---------------------------------------------------
# Priority Matrix
# ---------------------------------------------------

st.subheader("Priority Matrix")

priority = pd.DataFrame({

    "Opportunity":data["productivity_opportunities"],

    "Priority":["High"]*len(data["productivity_opportunities"])

})

st.dataframe(
    priority,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ---------------------------------------------------
# Management Recommendation
# ---------------------------------------------------

st.subheader("AI Recommendation")

st.info("""
Reduce walking distance by relocating frequently used components.

Introduce shadow boards for tools.

Improve workstation layout using 5S principles.

Reduce waiting between activities.

Standardize work instructions.

Monitor repetitive non-value-added activities continuously.
""")