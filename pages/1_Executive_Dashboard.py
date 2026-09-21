import streamlit as st
from pathlib import Path

from utils.loader import TimeStudyLoader


st.set_page_config(
    page_title="Executive Dashboard",
    layout="wide"
)

# --------------------------------------------------
# Load JSON
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "output" / "time_study.json"
        
loader = TimeStudyLoader(JSON_FILE)

loader.load()

data = loader.get_json()

overall = loader.get_overall()

df = loader.get_activity_dataframe()

summary = loader.get_summary()

lean = loader.get_lean()

opportunities = loader.get_opportunities()

operator_count = loader.get_operator_count()

operator_table = loader.get_operator_table()

# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("📊 Executive Dashboard")

st.caption("Industrial AI Time Study")

st.divider()

# --------------------------------------------------
# KPI
# --------------------------------------------------

va = overall["estimated_value_added_time"]

nva = overall["estimated_non_value_added_time"]

total = va + nva

if total > 0:
    va_percent = round((va / total) * 100, 1)
else:
    va_percent = 0

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric(
    "Processes",
    summary["total_processes"]
)

col2.metric(
    "Cycle Time",
    f'{overall["cycle_time_seconds"]} sec'
)

col3.metric(
    "Working",
    f'{overall["operator_working_time"]} sec'
)

col4.metric(
    "Walking",
    f'{overall["walking_time"]} sec'
)

col5.metric(
    "Idle",
    f'{overall["operator_idle_time"]} sec'
)

col6.metric(
    "VA %",
    f"{va_percent}%"
)

col7.metric(
    "Operators",
    operator_count
)

st.divider()

# --------------------------------------------------
# Operator Performance
#
# Every operator in the video is timed separately.
# --------------------------------------------------

st.subheader("👷 Operator Performance")

if operator_table.empty:

    st.info("No per-operator breakdown available for this analysis.")

else:

    if operator_count > 1:

        st.caption(
            f"{operator_count} operators detected — "
            "working, walking and idle time are calculated for each one."
        )

    else:

        st.caption("Single operator detected in this video.")

    st.dataframe(
        operator_table,
        use_container_width=True,
        hide_index=True
    )

    st.bar_chart(
        operator_table.set_index("Operator")[
            ["Working (sec)", "Walking (sec)", "Idle (sec)"]
        ]
    )

st.divider()

# --------------------------------------------------
# Video Summary
# --------------------------------------------------

st.subheader("🎥 Video Summary")

st.info(

    summary["video_summary"]

)

st.divider()

# --------------------------------------------------
# Lean Observation
# --------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Lean Observations")

    for item in lean:

        st.warning(item)

with right:

    st.subheader("Improvement Opportunities")

    for item in opportunities:

        st.success(item)

st.divider()

# --------------------------------------------------
# Management Summary
# --------------------------------------------------

st.subheader("Management Summary")

st.success(

    summary["management_summary"]

)

st.divider()

# --------------------------------------------------
# Activity Table
# --------------------------------------------------

st.subheader("Activities")

st.dataframe(

    df,

    use_container_width=True,

    hide_index=True

)