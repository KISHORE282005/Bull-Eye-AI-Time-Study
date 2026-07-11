import streamlit as st
from pathlib import Path
import pandas as pd

from utils.loader import TimeStudyLoader
from utils.export import export_excel, export_json, export_csv

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="AI Executive Report",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Executive Report")

st.caption("Industrial AI Time Study Report")

st.divider()

# ==========================================================
# LOAD JSON
# ==========================================================

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

# ==========================================================
# EXECUTIVE SUMMARY
# ==========================================================

st.header("Executive Summary")

st.success(summary["management_summary"])

st.divider()

# ==========================================================
# VIDEO SUMMARY
# ==========================================================

st.header("Video Summary")

st.info(summary["video_summary"])

st.divider()

# ==========================================================
# KPI SUMMARY
# ==========================================================

st.header("Overall Time Study")

k1,k2,k3,k4 = st.columns(4)

k1.metric(
    "Processes",
    summary["total_processes"]
)

k2.metric(
    "Cycle Time",
    f'{overall["cycle_time_seconds"]} sec'
)

k3.metric(
    "Working Time",
    f'{overall["operator_working_time"]} sec'
)

k4.metric(
    "Walking Time",
    f'{overall["walking_time"]} sec'
)

k1,k2,k3 = st.columns(3)

k1.metric(
    "Idle Time",
    f'{overall["operator_idle_time"]} sec'
)

k2.metric(
    "VA Time",
    f'{overall["estimated_value_added_time"]} sec'
)

k3.metric(
    "NVA Time",
    f'{overall["estimated_non_value_added_time"]} sec'
)

st.divider()

# ==========================================================
# LEAN OBSERVATIONS
# ==========================================================

st.header("Lean Observations")

for item in lean:

    st.warning(item)

st.divider()

# ==========================================================
# PRODUCTIVITY OPPORTUNITIES
# ==========================================================

st.header("Improvement Opportunities")

for item in opportunities:

    st.success(item)

st.divider()

# ==========================================================
# MANAGEMENT RECOMMENDATIONS
# ==========================================================

st.header("Management Recommendations")

recommendations = [

    "Reduce operator walking distance.",

    "Improve workstation layout.",

    "Reduce waiting time.",

    "Standardize work sequence.",

    "Improve material presentation.",

    "Eliminate repetitive NVA activities.",

    "Review TOCT of every operation."

]

for item in recommendations:

    st.success(item)

st.divider()
# ==========================================================
# TIME STUDY REPORT
# ==========================================================

st.header("Industrial Time Study Report")

report_df = df[[
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
]].copy()

report_df.columns = [
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
    report_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# TIME STUDY SUMMARY
# ==========================================================

st.header("Time Study Summary")

summary_df = pd.DataFrame({

    "Metric":[

        "Total Processes",

        "Total Duration",

        "Total TOCT",

        "Total NVA",

        "Total Repeat NVA"

    ],

    "Value":[

        len(df),

        round(df["duration"].sum(),2),

        round(df["toct"].sum(),2),

        round(df["nva"].sum(),2),

        round(df["r_nva"].sum(),2)

    ]

})

st.dataframe(

    summary_df,

    use_container_width=True,

    hide_index=True

)

st.divider()

# ==========================================================
# DOWNLOADS
# ==========================================================

st.header("Download Reports")

col1,col2,col3=st.columns(3)

with col1:

    st.download_button(

        label="📥 Download JSON",

        data=export_json(data),

        file_name="time_study.json",

        mime="application/json"

    )

with col2:

    st.download_button(

        label="📥 Download CSV",

        data=export_csv(df),

        file_name="Industrial_Time_Study.csv",

        mime="text/csv"

    )

with col3:

    excel = export_excel(

        df,

        overall,

        lean,

        opportunities,

        summary

    )

    st.download_button(

        label="📥 Download Excel",

        data=excel,

        file_name="Industrial_Time_Study_Report.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

st.divider()



