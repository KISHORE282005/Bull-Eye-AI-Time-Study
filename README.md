# 🏭 Industrial AI Time Study

**Bulls Eye — AI Time Study** is a Streamlit web application that automates industrial
**time & motion studies** from manufacturing shop-floor videos. Upload a video, and
Google **Gemini** analyzes the operator's activities, extracts each process with precise
timestamps, and the app runs standard **Industrial Engineering** calculations
(Duration, Operator times, TOCT, NVA, R-NVA, Value-Added %) to produce a full
executive report — downloadable as **JSON, CSV, and Excel**.

---

## ✨ Features

- **AI video analysis** — Gemini watches the manufacturing video and identifies each
  process step performed by the main operator, ignoring background activity.
- **Automatic time study** — computes process duration, operator working/waiting time,
  walking time, idle time, and value-added vs. non-value-added time.
- **Lean insights** — surfaces lean observations, productivity opportunities, and
  management recommendations.
- **Executive dashboard** — KPI cards, process tables, and summaries in the browser.
- **One-click exports** — download the report as JSON, CSV, or a formatted Excel workbook.
- **Automatic cleanup** — temporary video files and Gemini cloud uploads are deleted
  after analysis.

---

## 🧮 Time Study Metrics

| Metric | Meaning |
|--------|---------|
| **Duration** | Length of each process (`end − start` timestamp). |
| **Op1–Op5** | Working time per operator (up to 5 operators). |
| **WT1–WT5** | Waiting / walking / rework time per operator. |
| **TOCT** | Total Observed Cycle Time for the process. |
| **NVA** | Non-Value-Added time (waiting, walking, rework). |
| **R-NVA** | Repeated Non-Value-Added time (rework only). |
| **VA %** | Value-added share of total cycle time. |

Activities are auto-classified into **Working / Waiting / Walking / Rework** based on
the operation name (see [utils/calculations.py](utils/calculations.py)).

---

## 📦 Packages / Dependencies

Defined in [requirements.txt](requirements.txt):

| Package | Version | Purpose |
|---------|---------|---------|
| **streamlit** | `>=1.35.0` | Web UI framework — the entire front end and multi-page app. |
| **google-genai** | `>=1.0.0` | Google Gemini SDK — uploads the video and runs AI analysis. |
| **pandas** | `>=2.0.0` | Data tables, transformations, and CSV/Excel building. |
| **plotly** | `>=5.18.0` | Interactive charts and timelines. |
| **openpyxl** | `>=3.1.2` | Reads/writes the formatted `.xlsx` Excel reports. |
| **python-dotenv** | `>=1.0.0` | Loads the `GEMINI_API_KEY` from a `.env` file. |

> **Python 3.12** is used in development. Python **3.9+** is recommended.
> The Gemini model used is **`gemini-2.5-flash`** (set in [gemini/config.py](gemini/config.py)).

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or newer
- A Google Gemini API key — get one at
  [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 2. Install
```bash
# (recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 3. Configure your API key
```bash
copy .env.example .env       # Windows
# cp .env.example .env       # macOS / Linux
```
Then edit `.env` and set your key:
```
GEMINI_API_KEY=your_api_key_here
```

### 4. Run the app
```bash
streamlit run main.py
```
The app opens in your browser (usually at `http://localhost:8501`).

### 5. Use it
1. Upload a manufacturing video (`.mp4`, `.avi`, `.mov`, `.mkv`, up to **2 GB**).
2. Click **🔍 Analyze Video**.
3. Watch the 5-step progress: **Upload → Analyze → Parse → Calculate → Report**.
4. Review the dashboard and **download** the JSON / CSV / Excel reports.

---

## 🗂️ Project Structure

```
Industrial_AI_Time_Study/
├── main.py                     # App entry point — Streamlit navigation
├── app.py                      # Main page: upload, analyze, dashboard, downloads
├── requirements.txt            # Python dependencies
├── .env.example                # Template for the Gemini API key
│
├── gemini/                     # Google Gemini integration
│   ├── config.py               #   API client + model configuration
│   ├── uploader.py             #   Upload/delete video on Gemini cloud
│   ├── prompts.py              #   Industrial-engineering analysis prompt
│   ├── analyzer.py             #   Sends video + prompt to Gemini
│   ├── parser.py               #   Parses & validates Gemini's JSON response
│   └── report.py               #   Saves JSON / CSV / Excel to /output
│
├── utils/                      # Calculation & reporting helpers
│   ├── calculations.py         #   Time-study engine (Duration, TOCT, NVA...)
│   ├── loader.py               #   Loads/normalizes the saved JSON report
│   ├── export.py               #   Builds JSON/CSV/Excel exports
│   ├── charts.py               #   Plotly charts
│   ├── validator.py            #   Data validation
│   └── styles.py               #   UI styling helpers
│
├── pages/                      # Additional Streamlit pages
│   ├── 1_Executive_Dashboard.py
│   ├── 2_Process_Timeline.py
│   ├── 3_Process_Details.py
│   ├── 4_Lean_analysis.py
│   └── 5_AI_Report.py          #   Full executive report + downloads
│
├── assets/                     # Logo & CSS
├── docs/                       # Technical documentation
└── output/                     # Generated reports (created at runtime)
    ├── time_study.json
    ├── activities.csv
    └── Industrial_Time_Study_Report.xlsx
```

---

## ⚙️ How It Works

```
 Video ──► Gemini upload ──► AI analysis ──► JSON parse ──► IE calculations ──► Reports
           (uploader.py)     (analyzer.py)   (parser.py)    (calculations.py)   (report.py)
```

1. **Upload** — the video is saved to a temp file and pushed to Gemini cloud storage.
2. **Analyze** — Gemini returns each process with `start`/`end` timestamps as JSON.
3. **Parse** — the JSON is cleaned and validated for required fields.
4. **Calculate** — the time-study engine derives Duration, Op/WT columns, TOCT, NVA, R-NVA, and the overall summary.
5. **Report** — results are written to `/output` and shown on the dashboard.

---

## 🖥️ Deployment — Windows Server (Production)

> **Architecture note.** This is a **Streamlit** app. Streamlit runs its own web server
> and bundles the **frontend and backend into a single process** — there is no separate
> service to start. It does **not** run under `uvicorn` (uvicorn serves ASGI apps like
> FastAPI; Streamlit is not ASGI). The production setup below runs the one Streamlit
> process as a **Windows Service** and puts **IIS** in front of it as a reverse proxy, so
> users reach the app on **port 80/443** — not the internal dev port.

```
Browser (80 / 443)
      │
      ▼
   IIS  ── reverse proxy (ARR + URL Rewrite) + HTTPS
      │   →  http://127.0.0.1:8501
      ▼
   Streamlit app  ── Windows Service (NSSM), bound to localhost only
      │
      ▼
   gemini/ + utils/  ── backend logic (same process)
```

### 1. Install prerequisites on the server

- **Python 3.12** (64-bit) — from [python.org](https://www.python.org/downloads/windows/),
  check *"Add Python to PATH"* during install.
- **IIS** with the **Application Request Routing (ARR)** and **URL Rewrite** modules
  (install via Web Platform Installer or the standalone MSIs).
- **NSSM** (Non-Sucking Service Manager) — from [nssm.cc](https://nssm.cc/download),
  used to run Streamlit as a Windows Service.

### 2. Deploy the code and install dependencies

```powershell
# Copy the project to the server, e.g. C:\apps\Industrial_AI_Time_Study
cd C:\apps\Industrial_AI_Time_Study

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the environment (`.env`)

Create `C:\apps\Industrial_AI_Time_Study\.env`:

```
GEMINI_API_KEY="your_api_key_here"
ASSETS_DIR="C:/apps/Industrial_AI_Time_Study/assets"
```

### 4. Production `config.toml`

Ensure [.streamlit/config.toml](.streamlit/config.toml) has production settings — the app
binds to **localhost** (IIS is the only thing exposed publicly) and disables the dev tooling:

```toml
[server]
port = 8501
address = "127.0.0.1"      # localhost only — IIS handles public traffic
headless = true            # no auto-open browser, no "dev" prompts
maxUploadSize = 2048        # 2 GB uploads
enableCORS = false
enableXsrfProtection = true
runOnSave = false           # not a development server
```

### 5. Run Streamlit as a Windows Service (NSSM)

Running as a service means it starts on boot and restarts on failure — no console window,
no manual `streamlit run`.

```powershell
# Register the service (point NSSM at the venv's python + streamlit)
nssm install AITimeStudy "C:\apps\Industrial_AI_Time_Study\venv\Scripts\python.exe" ^
  "-m streamlit run C:\apps\Industrial_AI_Time_Study\main.py"

# Set the working directory so relative paths and .env resolve correctly
nssm set AITimeStudy AppDirectory "C:\apps\Industrial_AI_Time_Study"

# Start it
nssm start AITimeStudy
```

The app is now serving on `http://127.0.0.1:8501` (internal only). Manage it with
`nssm restart AITimeStudy` / `nssm stop AITimeStudy`, or from `services.msc`.

### 6. Put IIS in front as a reverse proxy (public port 80/443)

1. In **IIS Manager → server node → Application Request Routing Cache → Server Proxy
   Settings**, tick **Enable proxy**.
2. Create a website (or use *Default Web Site*) bound to port **80** (add an HTTPS
   binding on **443** with your TLS certificate).
3. Add a **URL Rewrite** inbound rule that forwards all traffic to Streamlit — this goes
   into the site's `web.config`:

```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="ReverseProxyToStreamlit" stopProcessing="true">
          <match url="(.*)" />
          <action type="Rewrite" url="http://127.0.0.1:8501/{R:1}" />
        </rule>
      </rules>
    </rewrite>
    <!-- Streamlit uses WebSockets; allow them through and raise the upload limit to 2 GB -->
    <webSocket enabled="true" />
    <security>
      <requestFiltering>
        <requestLimits maxAllowedContentLength="2147483648" />
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
```

### 7. Open the firewall

Allow inbound **80** and **443** in Windows Defender Firewall. Do **not** expose 8501 —
it stays bound to localhost behind IIS.

```powershell
New-NetFirewallRule -DisplayName "HTTP"  -Direction Inbound -Protocol TCP -LocalPort 80  -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
```

Users now reach the app at `http://<server>` (or `https://<server>` with TLS). ✅

> **Why not uvicorn?** If you specifically need a uvicorn/ASGI backend, the app would have
> to be re-architected — extract [gemini/](gemini/) and [utils/](utils/) into a FastAPI
> service and build a separate frontend. That's a full rewrite; the setup above keeps the
> existing single Streamlit app and is the correct production path for it.

---

## 📤 Output Files

| File | Description |
|------|-------------|
| `output/time_study.json` | Full structured analysis (processes + overall metrics). |
| `output/activities.csv` | Flat table of all processes and calculated columns. |
| `output/Industrial_Time_Study_Report.xlsx` | Formatted Excel workbook (Time Study + Overall Analysis sheets). |

---

## 📝 Notes

- Video files and Gemini cloud uploads are automatically deleted after each analysis.
- Maximum upload size is **2 GB**.
- Never commit your real `.env` file — only `.env.example` should be tracked.

---

## 📚 Documentation

Additional technical docs live in the [docs/](docs/) folder:
- [TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md)
- [LOGIC_DOCUMENT.md](docs/LOGIC_DOCUMENT.md)
- [SCHEMATIC.html](docs/SCHEMATIC.html)
