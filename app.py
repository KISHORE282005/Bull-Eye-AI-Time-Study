import base64
import os
import json
from pathlib import Path

import streamlit as st

# ==========================================================
# GEMINI MODULES
# ==========================================================

from gemini.uploader import upload_video
from gemini.analyzer import analyze_video
from gemini.parser import parse_json
from gemini.report import save_report
from utils.calculations import calculate_time_study

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Bull.com",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).parent

VIDEO_DIR = BASE_DIR / "videos"
OUTPUT_DIR = BASE_DIR / "output"

VIDEO_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

JSON_FILE = OUTPUT_DIR / "time_study.json"
EXCEL_FILE = OUTPUT_DIR / "Industrial_Time_Study_Report.xlsx"

# ==========================================================
# SESSION STATE
# ==========================================================

if "video_uploaded" not in st.session_state:
    st.session_state.video_uploaded = False

if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown("""
<style>

.main{
    background:#f5f7fb;
}

.title{
    font-size:36px;
    font-weight:bold;
    color:#0A4B8C;
}

.subtitle{
    font-size:18px;
    color:#666;
}

div[data-testid="metric-container"]{
    background:white;
    border-radius:12px;
    padding:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

.stButton>button{
    width:100%;
    height:55px;
    font-size:18px;
    font-weight:bold;
    border-radius:12px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER
# ==========================================================


def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = get_base64(r"C:\Users\kisho\Downloads\download.png")

st.markdown(f"""
<style>

.header-container{{
    display:flex;
    align-items:center;
    background:white;
    padding:20px 40px;
    border-radius:15px;
    box-shadow:0px 3px 10px rgba(0,0,0,.08);
}}

.logo{{
    width:320px;
}}

.separator{{
    width:2px;
    height:120px;
    background:#d9d9d9;
    margin:0px 35px;
}}

.title-container{{
    flex:1;
}}

.main-title{{
    font-size:64px;
    font-weight:800;
    color:#222;
    line-height:1;
}}

.sub-title{{
    font-size:64px;
    font-weight:800;
    color:#E31818;
    line-height:1;
}}

.caption{{
    margin-top:20px;
    font-size:26px;
    color:#555;
}}

</style>

<div class="header-container">

<img class="logo"
src="data:image/png;base64,{logo}">

<div class="separator"></div>

<div class="title-container">

<div class="main-title">
Bulls Eye
</div>

<div class="sub-title">
AI Time Study
</div>

""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("Industrial AI")

    st.success("System Ready")

    

    st.info(
        "Maximum Upload Size : **2 GB**"
    )

# ==========================================================
# VIDEO UPLOAD
# ==========================================================

st.header("🎥 Upload Manufacturing Video")

uploaded_video = st.file_uploader(
    "Upload Manufacturing Video",
    type=["mp4", "avi", "mov", "mkv"]
)

MAX_SIZE = 2 * 1024 * 1024 * 1024

if uploaded_video is not None:

    if uploaded_video.size > MAX_SIZE:

        st.error("❌ File size exceeds 2 GB.")

        st.stop()

    video_path = VIDEO_DIR / uploaded_video.name

    # Save only once
    if not video_path.exists():

        with open(video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())

    st.session_state.video_uploaded = True

    st.session_state.video_path = str(video_path)

    st.success("✅ Video uploaded successfully.")

    st.video(str(video_path))

    st.write(f"**File Name:** {uploaded_video.name}")

    st.write(
        f"**Size:** {round(uploaded_video.size/(1024*1024),2)} MB"
    )

st.divider()
# ==========================================================
# ANALYZE VIDEO
# ==========================================================

st.header("🚀 AI Analysis")

col1, col2 = st.columns([3, 1])

with col1:

    st.info(
        "After uploading the video, click **Analyze Video** to start the Industrial AI Time Study."
    )

with col2:

    analyze = st.button(
        "🚀 Analyze Video",
        type="primary",
        disabled=not st.session_state.video_uploaded
    )

# ==========================================================
# PROGRESS AREA
# ==========================================================

progress = st.progress(0)

status = st.empty()

log_box = st.empty()

# ==========================================================
# START ANALYSIS
# ==========================================================

if analyze:

    try:

        st.session_state.analysis_complete = False

        video_path = st.session_state.video_path

        if video_path is None:

            st.error("❌ No video found.")

            st.stop()

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------

        status.info("📤 Step 1 / 5 : Uploading video to Gemini...")

        progress.progress(10)

        log_box.write("Uploading video...")

        gemini_video = upload_video(video_path)

        progress.progress(25)

        # ----------------------------------------------------
        # STEP 2
        # ----------------------------------------------------

        status.info("🤖 Step 2 / 5 : Gemini is analyzing the manufacturing process...")

        log_box.write("Waiting for Gemini response...")

        response = analyze_video(gemini_video)

        progress.progress(60)

        # ----------------------------------------------------
        # STEP 3
        # ----------------------------------------------------

        status.info("📑 Step 3 / 5 : Parsing AI response...")

        log_box.write("Parsing JSON...")

        data = parse_json(response)

        progress.progress(70)


        # STEP 4 - Industrial Engineering Calculation Engine
# =====================================================

        status.info("⚙ Step 4 / 5 : Calculating Industrial Time Study...")
 
        log_box.write("Calculating Duration, Op1-Op5, WT1-WT5...")

        data = calculate_time_study(data)

        progress.progress(90)

        # ----------------------------------------------------
        # STEP 5
        # ----------------------------------------------------

        status.info("💾 Step 5 / 5 : Saving reports...")

        log_box.write("Generating Excel...")

        save_report(data)

        progress.progress(100)

        # ----------------------------------------------------
        # STEP 5
        # ----------------------------------------------------

        status.success("✅ Analysis Completed Successfully")

        log_box.success("Industrial AI Time Study Generated")

        progress.progress(100)

        st.session_state.analysis_complete = True

        st.balloons()

        st.rerun()

    except Exception as e:

        progress.progress(0)

        # Gemini overload

        if "503" in str(e):

            st.error(
                "🚦 Gemini servers are busy. Please wait a minute and click Analyze again."
            )

        elif "429" in str(e):

            st.error(
                "⚠ Gemini API quota exceeded."
            )

        else:

            st.error("❌ Analysis Failed")

            st.exception(e)

# ==========================================================
# DASHBOARD
# ==========================================================

st.divider()

if not JSON_FILE.exists():

    st.info(
        "👆 Upload a manufacturing video and click **Analyze Video**."
    )

    st.stop()

try:

    with open(

        JSON_FILE,

        "r",

        encoding="utf-8"

    ) as f:

        data = json.load(f)

except Exception:

    st.warning("No analysis available yet.")

    st.stop()

overall = data["overall_analysis"]

total = data["total_processes"]

cycle = overall["cycle_time_seconds"]

working = overall["operator_working_time"]

walking = overall["walking_time"]

idle = overall["operator_idle_time"]

va = overall["estimated_value_added_time"]

nva = overall["estimated_non_value_added_time"]

if (va + nva) > 0:

    va_percent = round(

        (va / (va + nva)) * 100,

        1

    )

else:

    va_percent = 0
    # ==========================================================
# EXECUTIVE KPI
# ==========================================================

st.subheader("📊 Executive KPI Dashboard")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric(
    "Processes",
    total
)

k2.metric(
    "Cycle Time",
    f"{cycle:.2f} sec"
)

k3.metric(
    "Working Time",
    f"{working:.2f} sec"
)

k4.metric(
    "Walking Time",
    f"{walking:.2f} sec"
)

k5.metric(
    "Idle Time",
    f"{idle:.2f} sec"
)

k6.metric(
    "VA %",
    f"{va_percent}%"
)

st.divider()

# ==========================================================
# VIDEO SUMMARY
# ==========================================================

st.subheader("🎥 Video Summary")

st.info(

    data.get(

        "video_summary",

        "No summary available."

    )

)

st.divider()
# ==========================================================
# LEAN OBSERVATIONS
# ==========================================================

st.subheader("📈 Lean Observations")

lean = data.get("lean_observations", [])

if len(lean) == 0:

    st.info("No Lean observations detected.")

else:

    for item in lean:

        st.warning(item)

st.divider()

# ==========================================================
# PRODUCTIVITY OPPORTUNITIES
# ==========================================================

st.subheader("🚀 Productivity Opportunities")

opportunities = data.get(

    "productivity_opportunities",

    []

)

if len(opportunities) == 0:

    st.info("No improvement opportunities available.")

else:

    for item in opportunities:

        st.success(item)

st.divider()

# ==========================================================
# PROCESS TABLE
# ==========================================================

st.subheader("📑 Industrial Time Study")

import pandas as pd

activities = data.get("activities", [])

if len(activities) == 0:

    st.warning("No activities detected.")

else:

    df = pd.DataFrame(activities)

    required_columns = [

        "process_no",

        "process_name",

        "process_operation",

        "process_description",

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

    for col in required_columns:

        if col not in df.columns:

            df[col] = 0

    df = df[required_columns]

    df.columns = [

        "Process No",

        "Process Name",

        "Process Operation",
        
        "Process Description",

        "Start Timestamp",

        "End Timestamp",

        "Duration",

        "Op1",

        "Op2",

        "Op3",

        "Op4",

        "Op5",

        "Op WT1",

        "Op WT2",

        "Op WT3",

        "Op WT4",

        "Op WT5",

        "TOCT",

        "NVA",

        "R-NVA"

    ]

    st.dataframe(

        df,

        use_container_width=True,

        hide_index=True,

        height=500

    )

st.divider()

# ==========================================================
# DOWNLOAD REPORTS
# ==========================================================

st.header("📥 Download Reports")

download_col1, download_col2, download_col3 = st.columns(3)

# ---------------- JSON ----------------

with download_col1:

    if JSON_FILE.exists():

        with open(JSON_FILE, "rb") as f:

            st.download_button(
                label="📄 Download JSON",
                data=f,
                file_name="time_study.json",
                mime="application/json",
                use_container_width=True
            )

# ---------------- CSV ----------------

with download_col2:

    csv_file = OUTPUT_DIR / "activities.csv"

    if csv_file.exists():

        with open(csv_file, "rb") as f:

            st.download_button(
                label="📊 Download CSV",
                data=f,
                file_name="activities.csv",
                mime="text/csv",
                use_container_width=True
            )

# ---------------- Excel ----------------

with download_col3:

    if EXCEL_FILE.exists():

        with open(EXCEL_FILE, "rb") as f:

            st.download_button(
                label="📗 Download Excel",
                data=f,
                file_name="Industrial_Time_Study_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

st.divider()



