# Bulls Eye — AI Time Study
## Logic Document — Calculation Engine, Classification Rules & Formulas

This document explains **exactly how the numbers are produced**. The AI (Gemini) only supplies raw process timestamps; every metric below is computed deterministically by [utils/calculations.py](../utils/calculations.py) via the entry point `calculate_time_study(data)`.

---

## 1. Engine Pipeline

`calculate_time_study(data)` runs five ordered stages on the `activities` list:

```
1. validate_activity()          → parse timestamps, compute duration, classify type
2. update_operator_columns()    → route duration into Op1–Op5 or WT1–WT5
3. calculate_process_metrics()  → compute TOCT, NVA, R-NVA per process
4. calculate_overall_analysis() → aggregate cycle / working / walking / idle / VA / NVA
5. (write back) data["activities"], data["overall_analysis"], data["total_processes"]
```

Each stage is idempotent: it **resets** its output columns to `0.0` before writing, so re-running never double-counts.

---

## 2. Time Parsing

### 2.1 `timestamp_to_seconds(ts)`
Converts `HH:MM:SS.sss` (or `HH:MM:SS`) into float seconds.

```
seconds = hours*3600 + minutes*60 + seconds + microseconds/1_000_000
```
- Empty / malformed input → `0.0` (never raises).
- Example: `00:01:15.250` → **75.25 s**

### 2.2 `seconds_to_timestamp(s)`
Inverse conversion back to `HH:MM:SS.sss`; negative values are clamped to 0.

---

## 3. Duration

`calculate_duration(start, end)`:

```
duration = round( to_seconds(end) − to_seconds(start), 3 )
if duration < 0:  duration = 0
```

**Rule:** duration is always ≥ 0. A reversed or equal pair yields 0.

---

## 4. Activity Classification

`classify_activity(process_operation)` maps the free-text `process_operation` string to one of four **activity types** using case-insensitive substring matching. The **order of checks matters**: Working → Waiting → Walking → Rework. First match wins; no match → `"Working"` (default).

| Activity Type | Trigger keywords (substring, case-insensitive) |
|---------------|------------------------------------------------|
| **Working** | Assembly, Bolt Tightening, Fastening, Pick Part, Place Part, Loading, Unloading, Machine Operation, Inspection, Testing, Welding, Grinding, Painting, Material Handling |
| **Waiting** | Waiting, Searching, Searching Tool, Searching Material, Machine Delay, Material Delay, Talking, Idle |
| **Walking** | Walking, Transportation, Move, Walking to Machine, Walking to Rack |
| **Rework** | Rework, Repeat Inspection, Repeat Tightening, Repeat Assembly |

> ⚠️ **Ordering caveat:** because Working is tested first, an operation like *"Repeat Inspection"* contains "Inspection" (Working) and would classify as **Working**, not Rework. Similarly *"Repeat Assembly"* → Working. If Rework detection is important, reorder the checks or make keywords more specific.

---

## 5. Operator Columns (Op1–Op5 / WT1–WT5)

`update_operator_columns(activities)` splits each activity's duration into an operator-specific column based on **activity type** and **operator id**.

- All 10 columns (`op1..op5`, `op_wt1..op_wt5`) are reset to `0.0` each pass.
- **Working** duration → `opN` (N = operator number).
- **Waiting / Walking / Rework** duration → `op_wtN` (working-loss column).

```
if activity_type == "Working":
    op{N}    = round(duration, 3)      # productive time
else:                                   # Waiting / Walking / Rework
    op_wt{N} = round(duration, 3)      # lost / non-productive time
```

Default operator is `"Operator 1"`, so in single-operator studies only `op1` / `op_wt1` are populated.

---

## 6. Per-Process Metrics (TOCT, NVA, R-NVA)

`calculate_process_metrics(activities)` — reset all three to `0.0`, then:

| Activity Type | TOCT | NVA | R-NVA |
|---------------|:----:|:---:|:-----:|
| **Working** | duration | 0 | 0 |
| **Waiting** | duration | duration | 0 |
| **Walking** | duration | duration | 0 |
| **Rework**  | duration | duration | duration |

**Definitions**
- **TOCT** (*Total Observed Cycle Time*) = the process's duration, always. So `Σ TOCT = Σ duration = cycle time`.
- **NVA** (*Non-Value-Added*) = the duration whenever the activity is Waiting, Walking, or Rework (i.e. anything that isn't Working).
- **R-NVA** (*Repeat Non-Value-Added*) = the duration only for Rework activities — a subset of NVA that quantifies waste caused by doing work twice.

Invariant hierarchy: `R-NVA ≤ NVA ≤ TOCT = duration`.

---

## 7. Overall Analysis (aggregate)

`calculate_overall_analysis(activities)` sums durations by type across all processes:

| Output key | Formula |
|------------|---------|
| `cycle_time_seconds` | Σ duration (all activities) |
| `operator_working_time` | Σ duration where type = Working |
| `walking_time` | Σ duration where type = Walking |
| `operator_idle_time` | Σ duration where type = Waiting |
| `inspection_time` | 0.0 *(reserved / not yet computed)* |
| `estimated_value_added_time` (VA) | = `operator_working_time` |
| `estimated_non_value_added_time` (NVA) | Σ duration where type ∈ {Waiting, Walking, Rework} |

All results are `round(..., 3)`.

### Derived KPI (in the pages, not the engine)
```
VA%  =  VA / (VA + NVA) × 100          # rounded to 1 decimal; 0 if VA+NVA == 0
```
Shown in the Executive KPI row and the AI Insights section of [app.py](../app.py).

---

## 8. Validation Rules (`utils/validator.py`)

Independent sanity checks used to flag inconsistent rows:

| Check | Rule |
|-------|------|
| `validate_duration` | `duration ≥ 0` |
| `validate_toct` | `|duration − toct| ≤ 0.01` (TOCT should equal duration) |
| `validate_nva` | `nva ≤ toct` |
| `validate_rnva` | `rnva ≤ nva` |

These encode the invariant `R-NVA ≤ NVA ≤ TOCT` from §6.

---

## 9. Worked Example

Suppose Gemini returns three activities:

| # | operation | start | end |
|---|-----------|-------|-----|
| 1 | Assembly | 00:00:00.000 | 00:00:10.000 |
| 2 | Walking to Rack | 00:00:10.000 | 00:00:14.000 |
| 3 | Waiting | 00:00:14.000 | 00:00:20.000 |

**Stage 1 — duration & type**

| # | duration | type |
|---|----------|------|
| 1 | 10.0 | Working |
| 2 | 4.0 | Walking |
| 3 | 6.0 | Waiting |

**Stage 2 — operator columns** (all Operator 1)

| # | op1 | op_wt1 |
|---|-----|--------|
| 1 | 10.0 | 0 |
| 2 | 0 | 4.0 |
| 3 | 0 | 6.0 |

**Stage 3 — process metrics**

| # | TOCT | NVA | R-NVA |
|---|------|-----|-------|
| 1 | 10.0 | 0 | 0 |
| 2 | 4.0 | 4.0 | 0 |
| 3 | 6.0 | 6.0 | 0 |

**Stage 4 — overall**

```
cycle_time_seconds      = 10 + 4 + 6 = 20.0
operator_working_time   = 10.0        (VA)
walking_time            = 4.0
operator_idle_time      = 6.0
non_value_added_time    = 4 + 6 = 10.0 (NVA)

VA% = 10 / (10 + 10) × 100 = 50.0%
```

**Interpretation:** of a 20-second cycle, only 50% is value-added; 10 s is waste (4 s walking + 6 s waiting) — the primary improvement targets flagged in the dashboard.

---

## 10. Design Principles

1. **AI observes, code computes.** Gemini never does arithmetic (prompt rule 11), so metrics are deterministic, testable, and auditable.
2. **Everything derives from duration.** Every metric is a bucketed sum of process durations — no hidden weighting.
3. **Idempotent stages.** Output columns are reset before each computation; safe to re-run.
4. **Fail-safe parsing.** Bad timestamps degrade to 0 rather than crashing the pipeline.
5. **Waste hierarchy.** `R-NVA ⊆ NVA ⊆ TOCT` gives a consistent lean-analysis basis (walking + waiting + rework = the non-value-added opportunity).
