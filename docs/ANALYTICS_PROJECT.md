# Bulls Eye — AI Time Study
## Analytics Project Document
### Automation of Intelligent Analysis

> **Product:** Industrial AI Time Study
> **Owner:** Bull Machine
> **Domain:** Industrial Engineering / Lean Manufacturing / Work-Study Automation
> **Stack:** Python · Streamlit · Google Gemini 2.5 Flash (`google-genai`) · Pandas · Plotly · OpenPyXL
> **Related docs:** [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) · [LOGIC_DOCUMENT.md](LOGIC_DOCUMENT.md)

---

## 1. Problem Objectives

### 1.1 Background

A conventional **time & motion study** requires an industrial engineer to stand on the shop
floor with a stopwatch, manually record the start and end of every operation, classify each
activity, and hand-calculate cycle time and waste. This is slow, expensive, subjective, and
non-repeatable — two engineers observing the same operator frequently produce different
numbers.

This project **automates the entire study** from a single shop-floor video.

### 1.2 Statement of Objectives

Six objectives are defined for this project:

| # | Objective | Description |
|---|-----------|-------------|
| **O1** | **Automated process segmentation** | Automatically detect and segment each distinct manufacturing process performed by the operator in a video, with precise start/end timestamps. |
| **O2** | **Activity classification** | Classify every detected process into one of four work-study categories — **Working, Waiting, Walking, Rework**. |
| **O3** | **Time-study computation** | Deterministically compute all standard IE metrics: Duration, Operator times (Op1–Op5), Waiting times (WT1–WT5), TOCT, NVA and R-NVA. |
| **O4** | **Value-added analysis** | Quantify overall cycle time and split it into **Value-Added (VA)** vs **Non-Value-Added (NVA)** time, and report the VA percentage. |
| **O5** | **Lean insight generation** | Generate qualitative lean observations, productivity opportunities, and a management summary from the observed process. |
| **O6** | **Automated reporting** | Produce auditable, downloadable reports (JSON, CSV, formatted Excel) and interactive dashboards without manual data entry. |

### 1.3 Description of the Analysis Performed

The analysis is a **hybrid two-stage pipeline** — an AI *perception* stage followed by a
deterministic *computation* stage:

```
STAGE 1 — PERCEPTION (AI, non-deterministic)
   Video ──► Gemini 2.5 Flash (multimodal vision-language model)
             "Act as an Industrial Engineering Expert"
             Output: JSON list of processes + start/end timestamps ONLY

STAGE 2 — COMPUTATION (rule-based, fully deterministic)
   JSON ──► Keyword classification  (Working / Waiting / Walking / Rework)
        ──► Duration & operator-column arithmetic
        ──► TOCT / NVA / R-NVA per process
        ──► Aggregation into overall KPIs
        ──► Validation + reporting
```

**Critical design decision:** the AI is explicitly forbidden (prompt rule 11 in
[gemini/prompts.py](../gemini/prompts.py)) from performing *any* arithmetic. It only
**observes and reports timestamps**. Every number in the final report is computed by
deterministic Python in [utils/calculations.py](../utils/calculations.py).

This matters analytically because it makes the output **auditable and reproducible** — the
same JSON always yields identical metrics, and the AI's error surface is confined to
*perception* (did it see the right process boundaries?) rather than *calculation*.

The analysis types performed are:

- **Descriptive** — what happened: process list, durations, cycle time, utilization split.
- **Diagnostic** — why the cycle time is what it is: NVA/R-NVA breakdown by waste category.
- **Prescriptive** — what to do: lean observations, improvement opportunities, and
  management recommendations.

### 1.4 Features / Input Variables

**Level 1 — Raw input (extracted by the model from video):**

| Variable | Type | Description |
|----------|------|-------------|
| `process_no` | Integer | Sequential process identifier. |
| `process_name` | Categorical (free text) | Name of the manufacturing process. |
| `process_operation` | Categorical (free text) | Operation type — **the key predictor for classification**. |
| `process_description` | Text | Narrative description of what the operator did. |
| `start_timestamp` | Temporal (`HH:MM:SS.sss`) | When the operator begins the process. |
| `end_timestamp` | Temporal (`HH:MM:SS.sss`) | When the operator completes the process. |

**Level 2 — Derived / engineered features:**

| Variable | Type | Derivation |
|----------|------|------------|
| `duration` | Continuous (seconds) | `end_timestamp − start_timestamp` |
| `activity_type` | Categorical (4 classes) | Keyword classification of `process_operation` |
| `operator` | Categorical | Operator assignment (defaults to `Operator 1`) |

### 1.5 Outcome / Target (Class) Variables

The project has **one categorical class variable** and a set of **continuous outcome
variables**.

**Primary class (target) variable:**

| Variable | Classes | Meaning |
|----------|---------|---------|
| `activity_type` | `Working` · `Waiting` · `Walking` · `Rework` | Work-study category driving all downstream waste math. |

**Continuous outcome variables (per process):**

| Variable | Unit | Definition |
|----------|------|------------|
| `duration` | seconds | Length of the process. |
| `op1`–`op5` | seconds | Working time routed to the responsible operator. |
| `op_wt1`–`op_wt5` | seconds | Waiting/walking/rework time per operator. |
| `toct` | seconds | Total Observed Cycle Time for the process. |
| `nva` | seconds | Non-Value-Added time. |
| `r_nva` | seconds | Repeated (rework) Non-Value-Added time. |

**Aggregate outcome variables (per study):**

`cycle_time_seconds`, `operator_working_time`, `walking_time`, `operator_idle_time`,
`inspection_time`, `estimated_value_added_time`, `estimated_non_value_added_time`, and the
derived **VA %**.

---

## 2. Extraction and Generation of Dataset

### 2.1 Users of the System

| User | Role in the system | What they consume |
|------|--------------------|-------------------|
| **Industrial / Manufacturing Engineer** | Primary user — uploads video, validates results | Full process table, TOCT/NVA columns, Excel export |
| **Production Supervisor** | Reviews line performance | Executive KPI dashboard, timeline |
| **Lean / CI Specialist** | Identifies waste and improvement projects | Lean observations, NVA & R-NVA analysis |
| **Plant Management** | Decision making | Executive summary, VA %, recommendations |

### 2.2 Source of Data

The dataset is **generated, not collected from an existing repository**. There is no
pre-existing labelled corpus — each study creates its own dataset from a primary
observation.

| Property | Specification |
|----------|---------------|
| **Primary source** | Shop-floor video recording of a manufacturing operation |
| **Formats accepted** | `.mp4`, `.avi`, `.mov`, `.mkv` |
| **Maximum size** | 2 GB (`maxUploadSize = 2048` in [.streamlit/config.toml](../.streamlit/config.toml)) |
| **Unit of observation** | One manufacturing process step performed by the main operator |
| **Sampling frame** | The main operator only — background personnel are excluded by design |
| **Generated dataset** | `output/time_study.json`, `output/activities.csv`, `output/{video_name}_Time_Study_Report.xlsx` |

### 2.3 ETL Procedure

```
┌─────────────────────────────────────────────────────────────────┐
│  EXTRACT                                                        │
├─────────────────────────────────────────────────────────────────┤
│  E1. User uploads video via Streamlit  ......... app.py          │
│  E2. Saved to a temporary file (tempfile.NamedTemporaryFile)     │
│  E3. Uploaded to Gemini File API  .............. gemini/uploader │
│      → poll file.state until PROCESSING completes               │
│  E4. Inference: prompt + video → raw JSON text   gemini/analyzer │
│      → raw response archived to output/gemini_response.txt      │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  TRANSFORM                                                      │
├─────────────────────────────────────────────────────────────────┤
│  T1. Strip markdown fences, json.loads()  ...... gemini/parser   │
│  T2. Schema validation — required fields present                │
│  T3. Timestamp → seconds; compute duration  .... utils/calc      │
│  T4. Classify activity_type (4 classes)                          │
│  T5. Route duration into Op1–Op5 / WT1–WT5                       │
│  T6. Compute TOCT, NVA, R-NVA per process                        │
│  T7. Aggregate overall analysis KPIs                             │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LOAD                                                           │
├─────────────────────────────────────────────────────────────────┤
│  L1. Write output/time_study.json  ............. gemini/report   │
│  L2. Write output/activities.csv                                 │
│  L3. Write styled Excel workbook (2 sheets)                      │
│  L4. Render dashboards  ........................ app.py, pages/  │
│  L5. CLEANUP — delete temp video + Gemini cloud file             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Dataset Schema (generated)

Each record in `activities[]` is a single process with **20 attributes** — 6 extracted,
14 computed. The overall study record adds 7 aggregate KPIs plus `video_summary`,
`management_summary`, `lean_observations[]` and `productivity_opportunities[]`.

### 2.5 Data Governance

- The video is held only in a **temporary file** and is deleted in the `finally` block
  after analysis.
- The Gemini cloud copy is deleted via `delete_gemini_file()` after inference.
- No personally identifiable operator data is stored — operators are referenced only as
  `Operator 1`–`Operator 5`.

---

## 3. Filtration and Dimensionality Reduction of Dataset

### 3.1 Noise Identification

Noise enters this pipeline from three distinct sources:

| Source | Noise type | Example |
|--------|-----------|---------|
| **Visual (scene)** | Irrelevant subjects and motion | Background workers, passers-by, forklifts, camera shake |
| **Model output** | Format & schema noise | Markdown fences around JSON, missing fields, hallucinated keys |
| **Numeric** | Invalid values | Malformed timestamps, `end < start`, negative durations, NVA > TOCT |

### 3.2 Filtration Techniques Applied

**(a) Visual noise — filtered at the prompt (source filtering)**

The prompt constrains the model's attention *before* data is generated
([gemini/prompts.py](../gemini/prompts.py)):

```
Rule 4. Analyze ONLY the main operator performing the manufacturing process.
Rule 5. Ignore background people and unrelated movements.
```

This is the most effective filter in the system — it removes irrelevant subjects at the
point of extraction rather than cleaning them out afterwards.

**(b) Format noise — filtered at parse time**

[gemini/parser.py](../gemini/parser.py) strips ```` ```json ```` fences and validates that
every activity carries all six required fields, raising a descriptive error otherwise.

**(c) Numeric noise — filtered at calculation time**

[utils/calculations.py](../utils/calculations.py) applies defensive filtering:

| Guard | Behaviour |
|-------|-----------|
| `timestamp_to_seconds()` | Malformed/empty timestamp → `0.0`, never raises |
| `calculate_duration()` | Negative duration clamped to `0` |
| `seconds_to_timestamp()` | Negative seconds clamped to `0` |
| `validate_activity()` | `setdefault()` fills every missing field |
| Column resets | All Op/WT/TOCT/NVA columns reset to `0.0` before write → no double-counting |

**(d) Post-hoc consistency filtering — [utils/validator.py](../utils/validator.py)**

Four integrity rules flag records that violate work-study logic:

| Rule | Constraint | Flag raised |
|------|-----------|-------------|
| `validate_duration` | `duration ≥ 0` | *Negative Duration* |
| `validate_toct` | `|duration − toct| ≤ 0.01` | *TOCT Mismatch* |
| `validate_nva` | `nva ≤ toct` | *NVA > TOCT* |
| `validate_rnva` | `r_nva ≤ nva` | *R-NVA > NVA* |

### 3.3 Dimensionality Reduction

Four reduction techniques are applied. Note that they are **semantic and structural**, not
statistical — see §3.4 for why.

**(a) Modality reduction (the largest reduction in the system)**

A 2 GB video at 30 fps is on the order of 10⁴–10⁵ frames × millions of pixels. The
vision-language model reduces this to a compact structured table of ~20 process records ×
6 fields.

```
~10^9 pixel values   ──►   ~120 structured values
                   (≈ 7 orders of magnitude reduction)
```

**(b) Categorical cardinality reduction — free text → 4 classes**

`process_operation` is unbounded free text. `classify_activity()` maps it onto a
**4-class categorical variable** using a curated keyword lexicon of ~30 terms:

| Class | Lexicon size | Sample terms |
|-------|--------------|--------------|
| `Working` | 14 | Assembly, Bolt Tightening, Welding, Grinding, Inspection, Material Handling |
| `Waiting` | 8 | Waiting, Searching Tool, Machine Delay, Idle, Talking |
| `Walking` | 5 | Walking, Transportation, Move, Walking to Rack |
| `Rework` | 4 | Rework, Repeat Inspection, Repeat Assembly |

Unbounded text cardinality → **4 levels**. This is the single most important feature
transformation, because all NVA/R-NVA arithmetic keys off this class.

**(c) Feature projection / column selection**

`REPORT_COLUMNS` in [utils/export.py](../utils/export.py) projects the working DataFrame
down to a fixed **19-column** report schema, dropping intermediate fields
(`activity_type`, `operator`, `process_description`, `waste_type`, `value_added`) that are
not needed in the deliverable.

**(d) Aggregation — 20 columns × N processes → 7 KPIs**

`calculate_overall_analysis()` collapses the entire process table into a 7-metric executive
vector: cycle time, working, walking, idle, inspection, VA and NVA time.

### 3.4 On PCA / Statistical Reduction

**Classical dimensionality-reduction techniques (PCA, LDA, t-SNE, SVD) are deliberately
not applied.** This is a justified design decision, not an omission:

1. **Low feature count.** After extraction the dataset has ~19 columns, most of which are
   already sparse-by-construction (Op1–Op5 and WT1–WT5 are mutually exclusive — exactly one
   is non-zero per row).
2. **Interpretability is mandatory.** A time study is an audit artefact. Principal
   components are linear blends with no physical meaning — an engineer cannot defend
   "PC1 = 4.2" to a plant manager, but can defend "Walking time = 12.4 s".
3. **Additive semantics must be preserved.** TOCT, NVA and R-NVA must sum exactly.
   Projection into an orthogonal component space destroys that additivity.
4. **Sparsity is intentional.** The Op/WT column layout mirrors the standard printed
   time-study sheet; compressing it would break the deliverable format.

> If the system were later extended to **cross-study analytics** (e.g. clustering hundreds of
> historical studies to find recurring waste patterns), PCA or t-SNE would become
> appropriate at *that* aggregate layer — not at the per-process layer documented here.

---

## 4. Model Specification

### 4.1 Technique Selected

The system uses a **hybrid architecture** combining a deep-learning perception model with a
deterministic symbolic engine.

| Layer | Technique | Component |
|-------|-----------|-----------|
| **Perception** | **Multimodal Vision-Language Transformer (Deep Learning)** — Google **Gemini 2.5 Flash**, applied **zero-shot** via prompt engineering | [gemini/analyzer.py](../gemini/analyzer.py) |
| **Classification** | **Rule-based / lexicon keyword classifier** (deterministic symbolic ML) | `classify_activity()` |
| **Computation** | **Deterministic arithmetic engine** (no learning) | [utils/calculations.py](../utils/calculations.py) |
| **Validation** | **Rule-based constraint checking** | [utils/validator.py](../utils/validator.py) |

**Why a Vision-Language Transformer?** The core task — *temporal action segmentation with
semantic labelling of an untrimmed, long-form industrial video* — requires jointly
understanding **what** the operator is doing and **when** it starts and stops, then
expressing it in domain language. Transformer-based multimodal models are currently the
only practical approach that delivers this **without a labelled training corpus**.

**Why zero-shot / prompt-based rather than supervised training?** The decisive constraint is
**data availability**. Supervised temporal action segmentation would require thousands of
frame-level annotated manufacturing videos — precisely the manual labelling effort this
project exists to eliminate. Zero-shot inference removes the training-data bottleneck
entirely.

**Why a rule-based classifier for `activity_type` rather than a trained one?** With no
labelled dataset, and with only 4 target classes driven by a well-understood domain
vocabulary, a curated lexicon is more accurate, fully explainable, instantly auditable, and
trivially extensible by an engineer who does not write ML code.

### 4.2 Model Selection Criteria

The perception model was selected against eight weighted criteria:

| # | Criterion | Requirement | How Gemini 2.5 Flash satisfies it |
|---|-----------|-------------|-----------------------------------|
| **C1** | **Native video understanding** | Must process video directly, not sampled stills | Natively multimodal over video input |
| **C2** | **Long-context capacity** | Must reason over a full production cycle, up to 2 GB | Long context window handles extended video |
| **C3** | **Temporal grounding** | Must emit precise `HH:MM:SS.sss` boundaries | Returns frame-accurate timestamps |
| **C4** | **Zero-shot capability** | No labelled training data exists | Strong instruction-following without fine-tuning |
| **C5** | **Structured output** | Must return strictly parseable JSON | Reliable schema-constrained JSON generation |
| **C6** | **Latency & cost** | Analysis must complete in minutes at low per-study cost | *Flash* tier is optimised for speed/cost over the Pro tier |
| **C7** | **Domain steerability** | Must adopt an "Industrial Engineering Expert" persona | Responds to role + rule-based prompting |
| **C8** | **Managed infrastructure** | No GPU cluster on-premises | Fully managed cloud API |

### 4.3 Alternatives Considered and Rejected

| Alternative | Why rejected |
|-------------|--------------|
| **CNN + LSTM / 3D-CNN (I3D, SlowFast)** trained in-house | Requires a large frame-level annotated dataset; months of labelling; GPU training infrastructure |
| **YOLO + object tracking** | Detects *objects*, not semantic *processes*; cannot name an operation or infer intent |
| **Pose estimation (OpenPose / MediaPipe) + classifier** | Yields joint coordinates but still needs a labelled action classifier on top; brittle to occlusion common on shop floors |
| **Gemini Pro tier** | Higher accuracy ceiling but materially slower and costlier; Flash is sufficient for process-boundary detection |
| **Manual stopwatch study** | The baseline being replaced — slow, subjective, non-repeatable |

### 4.4 Model Configuration

```python
# gemini/config.py
MODEL = "gemini-3.6-flash"
client = genai.Client(api_key=API_KEY)
```

Inference is **single-shot**: one prompt + one video → one JSON response, archived to
`output/gemini_response.txt` for audit.

### 4.5 Evaluation Criteria

Because there is no ground-truth labelled test set, the model is evaluated by
**constraint satisfaction and expert review** rather than accuracy metrics:

| Criterion | Method |
|-----------|--------|
| **Schema validity** | `parse_json()` — all required fields present, JSON parseable |
| **Temporal validity** | `duration ≥ 0`; `end_timestamp > start_timestamp` |
| **Arithmetic consistency** | `TOCT == duration`; `NVA ≤ TOCT`; `R-NVA ≤ NVA` ([validator.py](../utils/validator.py)) |
| **Additivity** | `Σ duration == cycle_time_seconds` |
| **Face validity** | Industrial engineer reviews process boundaries against the source video |
| **Reproducibility** | Identical input JSON must always produce identical metrics (guaranteed — Stage 2 is deterministic) |

### 4.6 Known Limitations

- Process-boundary precision depends on video quality, camera angle, and occlusion.
- Operator attribution defaults to `Operator 1`; multi-operator studies require manual
  assignment before Op2–Op5 populate.
- `inspection_time` is currently reported as `0.0` in the aggregate engine.
- The keyword lexicon is English-language and may need extension for site-specific
  operation vocabulary.
- The model is non-deterministic — the same video may yield slightly different process
  boundaries across runs (mitigated by archiving every raw response).

---

## 5. Summary

| Section | Outcome |
|---------|---------|
| **Objectives** | 6 objectives (O1–O6): segmentation, classification, computation, VA analysis, lean insight, reporting |
| **Input variables** | 6 extracted + 3 engineered |
| **Target variables** | 1 class variable (`activity_type`, 4 levels) + 13 continuous outcomes + 7 aggregate KPIs |
| **Dataset** | Generated per-study from shop-floor video via a 3-phase ETL pipeline |
| **Filtration** | Prompt-level visual filtering, parse-level schema filtering, calculation-level numeric guards, post-hoc constraint validation |
| **Reduction** | Modality reduction (~10⁷×), free-text → 4 classes, 19-column projection, 7-KPI aggregation; PCA deliberately excluded for interpretability |
| **Model** | Hybrid — Gemini 2.5 Flash multimodal transformer (zero-shot) for perception + deterministic rule-based engine for all computation |
| **Selection criteria** | 8 criteria (C1–C8) led by native video support, temporal grounding, and zero-shot capability |
