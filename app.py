import json
import tempfile
from pathlib import Path
import base64
import pandas as pd
import streamlit as st

# ==========================================================
# GEMINI MODULES
# ==========================================================

from gemini.uploader import upload_video, delete_gemini_file
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
    initial_sidebar_state="expanded",
)

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>
    .main {
        background: #f5f7fb;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #0A4B8C;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
    }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    }
    .stButton > button {
        width: 100%;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# ==========================================================
# HEADER
# ==========================================================


def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = get_base64(r"D:\Industrial_AI_Time_Study\assets\logo.png")

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
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

JSON_FILE = OUTPUT_DIR / "time_study.json"
CSV_FILE = OUTPUT_DIR / "activities.csv"
EXCEL_FILE = OUTPUT_DIR / "Industrial_Time_Study_Report.xlsx"

# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULT_SESSION = {
    "video_uploaded": False,
    "video_path": None,
    "analysis_complete": False,
    "gemini_file": None,
}

for key, value in DEFAULT_SESSION.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# SIDEBAR - PROGRESS WIDGETS
# ==========================================================

with st.sidebar:
    st.header("⚙ Analysis Progress")
    status = st.empty()
    progress = st.progress(0)
    log_box = st.expander("📋 Logs", expanded=False)

# ==========================================================
# VIDEO UPLOAD
# ==========================================================

st.header("🎥 Upload Manufacturing Video")

uploaded_video = st.file_uploader(
    "Upload Manufacturing Video",
    type=["mp4", "avi", "mov", "mkv"],
    accept_multiple_files=False,
)

MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

if uploaded_video is not None:
    if uploaded_video.size > MAX_SIZE:
        st.error("❌ Maximum upload size is 2 GB.")
        st.stop()

    if st.session_state.video_path is None:
        with tempfile.NamedTemporaryFile(
            mode="wb", suffix=".mp4", delete=False
        ) as tmp:
            tmp.write(uploaded_video.getbuffer())
            st.session_state.video_path = tmp.name
        st.session_state.video_uploaded = True

    st.success("✅ Video uploaded successfully.")
    st.video(st.session_state.video_path)

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**File Name :** {uploaded_video.name}")
    with col2:
        st.write(
            f"**File Size :** {round(uploaded_video.size / (1024 * 1024), 2)} MB"
        )

    temp_size = round(
        Path(st.session_state.video_path).stat().st_size / (1024 * 1024), 2
    )
    st.info(f"📁 Temporary Processing File : {temp_size} MB")

st.divider()

# ==========================================================
# ANALYZE BUTTON
# ==========================================================

analyze = st.button(
    "🔍 Analyze Video",
    use_container_width=True,
    type="primary",
)

# ==========================================================
# START ANALYSIS
# ==========================================================

if analyze:
    video_path = st.session_state.video_path
    gemini_video = None

    try:
        st.session_state.analysis_complete = False

        if video_path is None:
            st.error("❌ No uploaded video found.")
            st.stop()

        # =====================================================
        # STEP 1
        # =====================================================

        status.info("📤 Step 1 / 5 : Uploading video to Gemini...")
        progress.progress(10)
        log_box.write("Uploading temporary video...")

        gemini_video = upload_video(video_path)
        st.session_state.gemini_file = gemini_video
        progress.progress(25)

        # =====================================================
        # STEP 2
        # =====================================================

        status.info("🤖 Step 2 / 5 : Gemini is analyzing the manufacturing process...")
        log_box.write("Waiting for Gemini response...")

        response = analyze_video(gemini_video)
        progress.progress(55)

        # =====================================================
        # STEP 3
        # =====================================================

        status.info("📑 Step 3 / 5 : Parsing AI response...")
        log_box.write("Parsing JSON response...")

        data = parse_json(response)
        progress.progress(70)

        # =====================================================
        # STEP 4
        # =====================================================

        status.info("⚙ Step 4 / 5 : Industrial Engineering Calculations...")
        log_box.write("Calculating Duration...")
        log_box.write("Calculating Op1 - Op5...")
        log_box.write("Calculating WT1 - WT5...")
        log_box.write("Calculating TOCT...")
        log_box.write("Calculating NVA...")
        log_box.write("Calculating R-NVA...")

        data = calculate_time_study(data)
        progress.progress(90)

        # =====================================================
        # STEP 5
        # =====================================================

        status.info("💾 Step 5 / 5 : Generating Reports...")
        log_box.write("Saving JSON...")
        log_box.write("Saving CSV...")
        log_box.write("Saving Excel...")

        save_report(data)
        progress.progress(100)

        status.success("✅ Analysis Completed Successfully")
        st.session_state.analysis_complete = True
        st.balloons()

    except Exception as e:
        progress.progress(0)

        if "503" in str(e):
            st.error("🚦 Gemini servers are busy. Please wait a minute and try again.")
        elif "429" in str(e):
            st.error("⚠ Gemini API quota exceeded.")
        else:
            st.error("❌ Analysis Failed")
            st.exception(e)

    finally:
        if gemini_video is not None:
            try:
                if hasattr(gemini_video, "name"):
                    delete_gemini_file(gemini_video.name)
                    print("Gemini file deleted.")
            except Exception as ex:
                print(f"Gemini cleanup failed : {ex}")

        if video_path:
            try:
                temp_video = Path(video_path)
                if temp_video.exists():
                    temp_video.unlink()
                    print("Temporary video deleted.")
            except Exception as ex:
                print(f"Temporary file cleanup failed : {ex}")

        st.session_state.video_uploaded = False
        st.session_state.video_path = None
        st.session_state.gemini_file = None
        st.session_state.analysis_complete = False
        st.rerun()

# ==========================================================
# DASHBOARD
# ==========================================================

if not JSON_FILE.exists():
    st.info("👆 Upload a manufacturing video and click Analyze Video.")
    st.stop()

try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception:
    st.warning("No analysis available.")
    st.stop()

overall = data.get("overall_analysis", {})

total = data.get("total_processes", 0)
cycle = overall.get("cycle_time_seconds", 0)
working = overall.get("operator_working_time", 0)
walking = overall.get("walking_time", 0)
idle = overall.get("operator_idle_time", 0)
va = overall.get("estimated_value_added_time", 0)
nva = overall.get("estimated_non_value_added_time", 0)

va_percent = 0
if (va + nva) > 0:
    va_percent = round((va / (va + nva)) * 100, 1)

# ==========================================================
# KPI
# ==========================================================

st.subheader("📊 Executive KPI Dashboard")

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Processes", total)
k2.metric("Cycle Time", f"{cycle:.2f} sec")
k3.metric("Working Time", f"{working:.2f} sec")
k4.metric("Walking Time", f"{walking:.2f} sec")
k5.metric("Idle Time", f"{idle:.2f} sec")
k6.metric("VA %", f"{va_percent}%")

st.divider()

# ==========================================================
# SUMMARY
# ==========================================================

st.subheader("🎥 Video Summary")
st.info(data.get("video_summary", "No summary available."))

# ==========================================================
# LEAN
# ==========================================================

st.subheader("📈 Lean Observations")
for item in data.get("lean_observations", []):
    st.warning(item)

# ==========================================================
# OPPORTUNITIES
# ==========================================================

st.subheader("🚀 Productivity Opportunities")
for item in data.get("productivity_opportunities", []):
    st.success(item)

st.divider()

# ==========================================================
# PROCESS TABLE
# ==========================================================

st.subheader("📑 Industrial Time Study")

activities = data.get("activities", [])

if len(activities) == 0:
    st.warning("No activities detected.")
else:
    df = pd.DataFrame(activities)

    required_columns = [
        "process_no", "process_name", "process_operation",
        "process_description", "start_timestamp", "end_timestamp",
        "duration", "op1", "op2", "op3", "op4", "op5",
        "op_wt1", "op_wt2", "op_wt3", "op_wt4", "op_wt5",
        "toct", "nva", "r_nva",
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    df = df[required_columns]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=600,
    )

# ==========================================================
# DOWNLOAD REPORTS
# ==========================================================

st.divider()
st.header("📥 Download Reports")

c1, c2, c3 = st.columns(3)

with c1:
    if JSON_FILE.exists():
        with open(JSON_FILE, "rb") as f:
            st.download_button(
                "📄 Download JSON",
                data=f,
                file_name="time_study.json",
                mime="application/json",
                use_container_width=True,
            )

with c2:
    if CSV_FILE.exists():
        with open(CSV_FILE, "rb") as f:
            st.download_button(
                "📊 Download CSV",
                data=f,
                file_name="activities.csv",
                mime="text/csv",
                use_container_width=True,
            )

with c3:
    if EXCEL_FILE.exists():
        with open(EXCEL_FILE, "rb") as f:
            st.download_button(
                "📗 Download Excel",
                data=f,
                file_name="Industrial_Time_Study_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

# ==========================================================
# NEW ANALYSIS
# ==========================================================

st.divider()
st.header("🔄 New Analysis")
st.info("Click below to analyze another manufacturing video.")

if st.button("🆕 Start New Analysis", use_container_width=True):
    try:
        if st.session_state.video_path:
            temp_file = Path(st.session_state.video_path)
            if temp_file.exists():
                temp_file.unlink()
    except Exception:
        pass

    st.session_state.video_uploaded = False
    st.session_state.video_path = None
    st.session_state.analysis_complete = False
    st.session_state.gemini_file = None

    st.success("✅ Ready for next video.")
    st.rerun()
