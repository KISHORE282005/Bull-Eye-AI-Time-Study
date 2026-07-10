import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

from utils.loader import TimeStudyLoader

# ----------------------------------------------------
# Page Config
# ----------------------------------------------------

st.set_page_config(
    page_title="Process Timeline",
    page_icon="⏱",
    layout="wide"
)

st.title("⏱ Process Timeline")

st.caption("Industrial AI Time Study")

st.divider()

# ----------------------------------------------------
# Load JSON
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

JSON_FILE = BASE_DIR / "output" / "time_study.json"

loader = TimeStudyLoader(JSON_FILE)
loader.load()

df = loader.get_activity_dataframe()

# ----------------------------------------------------
# Convert Time
# ----------------------------------------------------

def convert_time(val):

    if pd.isna(val):
        return pd.Timestamp("1900-01-01")

    if isinstance(val, (int, float)):
        seconds = int(val)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return pd.Timestamp(f"2025-01-01 {h:02}:{m:02}:{s:02}")

    parts = str(val).split(":")

    if len(parts) == 2:

        m = int(parts[0])
        s = int(parts[1])

        return pd.Timestamp(
            f"2025-01-01 00:{m:02}:{s:02}"
        )

    if len(parts) == 3:

        h = int(parts[0])
        m = int(parts[1])
        s = int(parts[2])

        return pd.Timestamp(
            f"2025-01-01 {h:02}:{m:02}:{s:02}"
        )

    return pd.Timestamp("2025-01-01")

df["Start"] = df["start_time"].apply(convert_time)
df["Finish"] = df["end_time"].apply(convert_time)

df["duration_seconds"] = df["duration"]

# ----------------------------------------------------
# Timeline Chart
# ----------------------------------------------------

fig = px.timeline(
    df,
    x_start="Start",
    x_end="Finish",
    y="process_name",
    color="activity_type",
    hover_data=[
        "duration",
        "process_operation",
        "operator",
        "process_description"
    ],
    title="Process Timeline"
)

fig.update_yaxes(
    autorange="reversed"
)

fig.update_layout(
    height=700
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ----------------------------------------------------
# Timeline Table
# ----------------------------------------------------

st.subheader("Timeline Table")

timeline = df[
    [
        "process_no",
        "process_name",
        "start_time",
        "end_time",
        "duration_seconds",
        "value_added",
        "waste_type"
    ]
]

st.dataframe(
    timeline,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------------------------------
# Statistics
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Process Duration")

    duration_chart = px.bar(
        df,
        x="process_name",
        y="duration_seconds",
        text="duration_seconds",
        color="value_added"
    )

    st.plotly_chart(
        duration_chart,
        use_container_width=True
    )

with right:

    st.subheader("Activity Sequence")

    sequence = px.line(
        df,
        x="process_no",
        y="duration_seconds",
        markers=True
    )

    st.plotly_chart(
        sequence,
        use_container_width=True
    )

st.divider()

# ----------------------------------------------------
# Process Cards
# ----------------------------------------------------

st.subheader("Process Details")

for _, row in df.iterrows():

    with st.expander(
        f"Process {row['process_no']} - {row['process_name']}"
    ):

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                f"**Description:** {row['process_description']}"
            )

            st.write(
                f"**Operator Action:** {row['operator_action']}"
            )

            st.write(
                f"**Machine:** {row['machine_used']}"
            )

        with c2:

            st.write(
                f"**Start:** {row['start_time']}"
            )

            st.write(
                f"**End:** {row['end_time']}"
            )

            st.write(
                f"**Duration:** {row['duration_seconds']} sec"
            )

            st.write(
                f"**Confidence:** {row['confidence']}"
            )

            st.write(
                f"**Value Added:** {row['value_added']}"
            )

            st.write(
                f"**Waste Type:** {row['waste_type']}"
            )