# Bulls Eye — AI Time Study
## Technical Documentation

> **Product:** Industrial AI Time Study
> **Owner:** Bull Machine
> **Stack:** Python · Streamlit · Google Gemini (google-genai) · Pandas · Plotly · OpenPyXL
> **Purpose:** Upload a manufacturing video → AI extracts each process step with timestamps → an Industrial Engineering calculation engine computes cycle time, operator utilization, and Value-Added / Non-Value-Added metrics → interactive dashboards + downloadable Excel / CSV / JSON reports.

---

## 1. System Overview

The application is a **multi-page Streamlit web app**. A user uploads a shop-floor video (up to 2 GB). The video is sent to **Google Gemini 2.5 Flash**, which acts as an "Industrial Engineering Expert" and returns a structured JSON list of manufacturing processes, each with a name, operation, description, and start/end timestamps.

The AI **only observes and returns timestamps** — it deliberately does *not* do any math. All time-study calculations (duration, operator columns, TOCT, NVA, R-NVA, and overall analysis) are performed by a deterministic Python engine in [utils/calculations.py](../utils/calculations.py). This separation keeps the numbers auditable and reproducible.

Results are persisted to `output/time_study.json` and rendered across five dashboard pages plus a home page, and exported to Excel/CSV.

### High-level pipeline

```
Video (mp4/avi/mov/mkv)
        │
        ▼
[1] Upload to Gemini            gemini/uploader.py
        │
        ▼
[2] AI analysis (prompt)        gemini/analyzer.py + gemini/prompts.py
        │
        ▼
[3] Parse & validate JSON       gemini/parser.py
        │
        ▼
[4] Calculation engine          utils/calculations.py
        │
        ▼
[5] Save reports (JSON/XLSX/CSV) gemini/report.py
        │
        ▼
Dashboards (Streamlit pages)    app.py + pages/*.py
```

---

## 2. Architecture & Module Map

```
Industrial_AI_Time_Study/
├── app.py                       # Main entry page: upload, run pipeline, home dashboard
├── requirements.txt             # Python dependencies
├── .env / .env.example          # GEMINI_API_KEY configuration
├── .streamlit/config.toml       # Streamlit theming/config
│
├── gemini/                      # AI integration layer
│   ├── config.py                # Loads API key, defines client + MODEL
│   ├── uploader.py              # Uploads video, waits for Gemini file processing
│   ├── prompts.py               # TIME_STUDY_PROMPT (JSON schema + rules)
│   ├── analyzer.py              # Calls Gemini generate_content, saves raw response
│   ├── parser.py                # Strips markdown, json.loads, validates required fields
│   └── report.py                # Writes JSON, styled Excel, and CSV
│
├── utils/                       # Calculation + presentation helpers
│   ├── calculations.py          # ★ Time-study engine (duration, classify, metrics)
│   ├── loader.py                # TimeStudyLoader: reads JSON, builds DataFrames
│   ├── charts.py                # Plotly chart builders (VA/NVA, waste, gauges…)
│   ├── validator.py             # Sanity checks (duration≥0, NVA≤TOCT, R-NVA≤NVA)
│   ├── export.py                # In-memory Excel/CSV/JSON export for download buttons
│   └── styles.py                # Injected CSS
│
├── pages/                       # Streamlit multi-page dashboards
│   ├── 1_Executive_Dashboard.py # KPIs + charts (VA/NVA, waste, efficiency gauge)
│   ├── 2_Process_Timeline.py    # Gantt-style timeline of processes
│   ├── 3_Process_Details.py     # Searchable per-process detail table
│   ├── 4_Lean_analysis.py       # Lean waste analysis / observations
│   └── 5_AI_Report.py           # Executive report + download exports
│
├── assets/                      # logo.png, style.css
├── videos/                      # Uploaded source videos (runtime, git-ignored)
└── output/                      # Generated artifacts (runtime)
    ├── time_study.json          # Canonical result consumed by all pages
    ├── gemini_response.txt      # Raw AI response (debugging)
    ├── activities.csv
    └── Industrial_Time_Study_Report.xlsx
```

### Layer responsibilities

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| **Presentation** | `app.py`, `pages/*`, `utils/charts.py`, `utils/styles.py` | UI, upload widget, KPIs, charts, downloads |
| **AI Integration** | `gemini/config`, `uploader`, `analyzer`, `prompts`, `parser` | Talk to Gemini, get validated JSON of processes |
| **Domain / Calculation** | `utils/calculations.py`, `utils/validator.py` | Deterministic time-study math + sanity checks |
| **Persistence / Export** | `gemini/report.py`, `utils/loader.py`, `utils/export.py` | Read/write JSON, Excel, CSV |

---

## 3. Runtime Flow (app.py)

The main page drives the 5-step pipeline inside a `try/except` block (see [app.py:274-388](../app.py#L274-L388)):

| Step | UI progress | Function | Module |
|------|-------------|----------|--------|
| 1 | 10 → 25% | `upload_video(video_path)` | `gemini/uploader.py` |
| 2 | 60% | `analyze_video(gemini_video)` | `gemini/analyzer.py` |
| 3 | 70% | `parse_json(response)` | `gemini/parser.py` |
| 4 | 90% | `calculate_time_study(data)` | `utils/calculations.py` |
| 5 | 100% | `save_report(data)` | `gemini/report.py` |

**Session state** keeps `video_uploaded`, `video_path`, and `analysis_complete` across reruns. On success the app calls `st.balloons()` and `st.rerun()` to refresh the dashboard from the freshly written `output/time_study.json`.

**Error handling:** Gemini `503` (server busy) and `429` (quota exceeded) produce friendly messages; any other exception is surfaced with `st.exception(e)`.

---

## 4. Data Model

### 4.1 AI output (what Gemini returns)

Defined by `TIME_STUDY_PROMPT` in [gemini/prompts.py](../gemini/prompts.py). Gemini returns **only** these fields per activity:

```jsonc
{
  "video_summary": "…",
  "total_processes": 0,
  "activities": [
    {
      "process_no": 1,
      "process_name": "",
      "process_operation": "",       // e.g. "Assembly", "Walking", "Waiting"
      "process_description": "",
      "start_timestamp": "00:00:00.000",  // HH:MM:SS.sss
      "end_timestamp":   "00:00:00.000"
    }
  ],
  "overall_analysis": { … },         // present but zero-filled; recomputed by engine
  "lean_observations": [],
  "productivity_opportunities": [],
  "management_summary": ""
}
```

The prompt **explicitly forbids** the model from computing Duration, Op1–Op5, WT1–WT5, TOCT, NVA, or R-NVA (rule 11). It analyzes only the **main operator** and ignores background people (rules 4–5).

### 4.2 Engine-enriched activity (after calculations)

`calculate_time_study` adds the following computed fields to each activity:

| Field | Type | Meaning |
|-------|------|---------|
| `duration` | float (s) | `end − start`, floored at 0 |
| `activity_type` | str | Working / Waiting / Walking / Rework |
| `operator` | str | defaults to "Operator 1" |
| `op1`…`op5` | float (s) | Working time attributed to Operator N |
| `op_wt1`…`op_wt5` | float (s) | Non-working (wait/walk/rework) time for Operator N |
| `toct` | float (s) | Total Observed Cycle Time for the process |
| `nva` | float (s) | Non-Value-Added time |
| `r_nva` | float (s) | Repeat / rework Non-Value-Added time |

### 4.3 `overall_analysis` (recomputed)

| Key | Meaning |
|-----|---------|
| `cycle_time_seconds` | Σ duration of all activities |
| `operator_working_time` | Σ Working durations |
| `walking_time` | Σ Walking durations |
| `operator_idle_time` | Σ Waiting durations |
| `inspection_time` | reserved (0.0) |
| `estimated_value_added_time` | = operator_working_time |
| `estimated_non_value_added_time` | Σ (Waiting + Walking + Rework) |

`VA%` shown on dashboards = `VA / (VA + NVA) × 100`.

> **See [LOGIC_DOCUMENT.md](LOGIC_DOCUMENT.md) for the full formulas, classification keyword tables, and worked examples.**

---

## 5. Setup & Installation

### Prerequisites
- Python 3.10+
- A Google Gemini API key

### Install
```bash
# 1. Clone / open the project
cd Industrial_AI_Time_Study

# 2. (Recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure the API key
copy .env.example .env         # Windows
# cp .env.example .env         # macOS/Linux
#   then edit .env and set:
#   GEMINI_API_KEY=your_key_here

# 5. Run the app
streamlit run app.py
```

The app opens in the browser. Upload a video (mp4/avi/mov/mkv, ≤ 2 GB), click **🚀 Analyze Video**, and wait for the 5-step pipeline to finish.

### Dependencies (`requirements.txt`)
```
streamlit>=1.35.0
google-genai>=1.0.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.2
python-dotenv>=1.0.0
```

---

## 6. Configuration Notes & Known Constraints

- **Model:** `gemini-2.5-flash` — set in [gemini/config.py](../gemini/config.py). Change here to switch models.
- **API key** is required at import time; the app raises a `ValueError` on startup if `GEMINI_API_KEY` is missing.
- **Hard-coded logo path:** [app.py:106](../app.py#L106) reads a logo from `C:\Users\kisho\Downloads\download.png`. This will fail on other machines — consider switching to the bundled `assets/logo.png`.
- **Single-user / local file store:** Results live in `output/time_study.json`; every page reads the same file, so the app effectively shows the **most recent** analysis only.
- **Upload limit:** enforced at 2 GB in `app.py`; Streamlit's own `maxUploadSize` may also need raising in `.streamlit/config.toml`.
- **Operator attribution:** the current engine defaults every activity to "Operator 1" (the prompt analyzes only the main operator), so `op2`–`op5` / `op_wt2`–`op_wt5` remain 0 unless the data supplies an `operator` field.
- **`utils/export.py` vs `report.py`:** `export.py` uses slightly different column keys (`start_time`/`end_time`) than the engine (`start_timestamp`/`end_timestamp`) — keep these aligned when editing export logic.

---

## 7. Extending the System

| Goal | Where to change |
|------|-----------------|
| Add a new activity classification | `WORKING/WAITING/WALKING/REWORK` keyword lists in [utils/calculations.py](../utils/calculations.py) |
| Change what counts as Value-Added | `calculate_process_metrics` / `calculate_overall_analysis` |
| Support multiple operators | Add `operator` to the prompt schema + parser; engine already routes Op1–Op5 |
| New chart | Add a builder in `utils/charts.py`, call it from a page |
| New dashboard page | Add `pages/N_Name.py` (Streamlit auto-registers) |
| Tune AI behavior | `TIME_STUDY_PROMPT` in `gemini/prompts.py` |
| Switch model | `MODEL` in `gemini/config.py` |
