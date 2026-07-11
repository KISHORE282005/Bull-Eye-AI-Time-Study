import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

from utils.loader import TimeStudyLoader

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Process Details",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Process Details")

st.caption("Industrial AI Time Study")

st.divider()

# ==========================================================
# LOAD JSON
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "output" / "time_study.json"

loader = TimeStudyLoader(JSON_FILE)

loader.load()

df = loader.get_activity_dataframe()

# ==========================================================
# SEARCH
# ==========================================================

search = st.text_input(
    "🔍 Search Process Name"
)

if search:

    df = df[
        df["process_name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

# ==========================================================
# SUMMARY
# ==========================================================

st.subheader("Summary")

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Processes",
    len(df)
)

c2.metric(
    "Average Duration",
    round(df["duration"].mean(),2)
)

c3.metric(
    "Average TOCT",
    round(df["toct"].mean(),2)
)

c4.metric(
    "Average NVA",
    round(df["nva"].mean(),2)
)

st.divider()

# ==========================================================
# PROCESS TABLE
# ==========================================================

st.subheader("Time Study Report")

display_df = df[
[
    "process_no",
    "process_name",
    "process_operation",

    "start_timestamp",
    "end_timestamp",

    "duration",

    "op1",
    "op2",
    "op3",
    "op4",
    "op5",

    "op_wt1",
    "op_wt2",
    "op_wt3",
    "op_wt4",
    "op_wt5",

    "toct",
    "nva",
    "r_nva"
]
]

display_df.columns=[

    "Process No",

    "Process Name",

    "Process Operation",

    "Start Time",

    "End Time",

    "Duration",

    "Op1 (min)",

    "Op2 (min)",

    "Op3 (min)",

    "Op4 (min)",

    "Op5 (min)",

    "Op WT1 (min)",

    "Op WT2 (min)",

    "Op WT3 (min)",

    "Op WT4 (min)",

    "Op WT5 (min)",

    "TOCT (min)",

    "NVA (min)",

    "R-NVA (min)"

]

st.dataframe(

    display_df,

    use_container_width=True,

    hide_index=True

)

st.divider()

# ==========================================================
# DURATION CHART
# ==========================================================

st.subheader("Process Duration")

fig = px.bar(

    df,

    x="process_name",

    y="duration",

    text="duration",

    color="process_name"

)

fig.update_layout(

    xaxis_title="Process",

    yaxis_title="Duration (sec)"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# TOCT CHART
# ==========================================================

st.subheader("TOCT Comparison")

fig = px.bar(

    df,

    x="process_name",

    y="toct",

    text="toct",

    color="process_name"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# NVA CHART
# ==========================================================

st.subheader("Non Value Added Time")

fig = px.bar(

    df,

    x="process_name",

    y="nva",

    text="nva",

    color="process_name"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()

# ==========================================================
# R-NVA CHART
# ==========================================================

st.subheader("Repeat NVA")

fig = px.bar(

    df,

    x="process_name",

    y="r_nva",

    text="r_nva",

    color="process_name"

)

st.plotly_chart(

    fig,

    use_container_width=True

)

st.divider()