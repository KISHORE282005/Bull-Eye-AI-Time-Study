import re
from datetime import datetime
from collections import defaultdict
from utils.nva_reasons import assign_nva_reasons


# ============================================================
# TIMESTAMP TO SECONDS
# ============================================================

def timestamp_to_seconds(timestamp):
    """
    Convert timestamp (HH:MM:SS.sss) into seconds.

    Example:
    00:01:15.250 -> 75.25
    """

    if not timestamp:
        return 0.0

    try:

        timestamp = str(timestamp).strip()

        if "." in timestamp:

            t = datetime.strptime(
                timestamp,
                "%H:%M:%S.%f"
            )

        else:

            t = datetime.strptime(
                timestamp,
                "%H:%M:%S"
            )

        return (
            t.hour * 3600
            + t.minute * 60
            + t.second
            + (t.microsecond / 1000000)
        )

    except Exception:

        return 0.0


# ============================================================
# SECONDS TO TIMESTAMP
# ============================================================

def seconds_to_timestamp(seconds):
    """
    Convert seconds back into HH:MM:SS.sss
    """

    if seconds < 0:
        seconds = 0

    hours = int(seconds // 3600)

    seconds %= 3600

    minutes = int(seconds // 60)

    seconds %= 60

    return f"{hours:02}:{minutes:02}:{seconds:06.3f}"


# ============================================================
# CALCULATE DURATION
# ============================================================

def calculate_duration(start_timestamp, end_timestamp):

    print("--------------------------------")
    print("Start :", start_timestamp)
    print("End   :", end_timestamp)

    start = timestamp_to_seconds(start_timestamp)
    end = timestamp_to_seconds(end_timestamp)

    print("Start Seconds :", start)
    print("End Seconds   :", end)

    duration = round(end - start, 3)

    print("Duration :", duration)

    if duration < 0:
        duration = 0

    return duration
# ============================================================
# ACTIVITY GROUPS
# ============================================================

WORKING = [

    "Assembly",
    "Bolt Tightening",
    "Fastening",
    "Pick Part",
    "Place Part",
    "Loading",
    "Unloading",
    "Machine Operation",
    "Inspection",
    "Testing",
    "Welding",
    "Grinding",
    "Painting",
    "Material Handling"

]


WAITING = [

    "Waiting",
    "Searching",
    "Searching Tool",
    "Searching Material",
    "Machine Delay",
    "Material Delay",
    "Talking",
    "Idle"

]


WALKING = [

    "Walking",
    "Transportation",
    "Move",
    "Walking to Machine",
    "Walking to Rack"

]


REWORK = [

    "Rework",
    "Repeat Inspection",
    "Repeat Tightening",
    "Repeat Assembly"

]


# ============================================================
# ACTIVITY CLASSIFICATION
# ============================================================

def classify_activity(process_operation):
    """
    Classify process operation into
    Working / Waiting / Walking / Rework
    """

    if not process_operation:
        return "Working"

    operation = process_operation.lower().strip()

    # -----------------------------
    # Working
    # -----------------------------

    for item in WORKING:

        if item.lower() in operation:
            return "Working"

    # -----------------------------
    # Waiting
    # -----------------------------

    for item in WAITING:

        if item.lower() in operation:
            return "Waiting"

    # -----------------------------
    # Walking
    # -----------------------------

    for item in WALKING:

        if item.lower() in operation:
            return "Walking"

    # -----------------------------
    # Rework
    # -----------------------------

    for item in REWORK:

        if item.lower() in operation:
            return "Rework"

    # Default
    return "Working"


# ============================================================
# VALIDATE ACTIVITY
# ============================================================

def validate_activity(activity):
    """
    Validate one activity returned by Gemini
    and prepare it for calculation.
    """

    # -----------------------------------
    # Read timestamps from Gemini
    # -----------------------------------

    start_timestamp = activity.get(
        "start_timestamp",
        "00:00:00.000"
    )

    end_timestamp = activity.get(
        "end_timestamp",
        "00:00:00.000"
    )

    # -----------------------------------
    # Calculate duration
    # -----------------------------------

    duration = calculate_duration(
        start_timestamp,
        end_timestamp
    )

    activity["duration"] = duration

    # -----------------------------------
    # Classify activity
    # -----------------------------------

    activity["activity_type"] = classify_activity(

        activity.get(
            "process_operation",
            ""
        )

    )

    # -----------------------------------
    # Ensure required fields exist
    # -----------------------------------

    activity.setdefault("process_no", 0)
    activity.setdefault("process_name", "")
    activity.setdefault("process_operation", "")
    activity.setdefault("process_description", "")

    activity.setdefault("start_timestamp", start_timestamp)
    activity.setdefault("end_timestamp", end_timestamp)

    # -----------------------------------
    # Operator tag (never blank)
    # -----------------------------------

    operator = str(
        activity.get("operator", "") or ""
    ).strip()

    activity["operator"] = operator or "Operator 1"

    return activity
# ============================================================
# OPERATOR IDENTIFICATION
# ============================================================

MAX_OPERATORS = 5


def operator_name(index):
    """
    Operator index -> canonical tag. 2 -> "Operator 2"
    """

    return f"Operator {index}"


def extract_operator_index(raw):
    """
    Pull an operator number (1 to 5) out of whatever label the AI returned.

    "Operator 2" -> 2
    "operator2"  -> 2
    "OP 3"       -> 3
    "Operator B" -> 2

    Returns None when the label carries no usable number or letter.
    """

    text = str(raw or "").strip()

    if not text:
        return None

    # -----------------------------------
    # Numbered labels
    # -----------------------------------

    digits = re.findall(r"\d+", text)

    if digits:

        number = int(digits[0])

        if 1 <= number <= MAX_OPERATORS:
            return number

        return None

    # -----------------------------------
    # Lettered labels (Operator A / B / C)
    # -----------------------------------

    for letter in re.findall(r"\b([A-Za-z])\b", text):

        number = ord(letter.upper()) - ord("A") + 1

        if 1 <= number <= MAX_OPERATORS:
            return number

    return None


def assign_operator_indices(activities):
    """
    Give every activity a canonical operator tag plus an operator index.

    The prompt asks for "Operator 1" ... "Operator 5", but real responses
    also arrive as "operator2", "Op 3" or a free-text description. Every
    DISTINCT label is mapped to its own slot, so two operators are never
    collapsed into the same column and never lose their time.
    """

    mapping = {}

    used = set()

    # -----------------------------------
    # Pass 1 : labels that already carry a
    # number keep that exact slot.
    #
    # Different spellings of the same number
    # ("Operator 2", "operator2", "OP 2")
    # are the SAME person and MUST share one
    # slot, or their time gets split in two.
    # -----------------------------------

    for activity in activities:

        raw = str(activity.get("operator", "") or "").strip()

        key = raw.lower()

        if not key or key in mapping:
            continue

        index = extract_operator_index(raw)

        if index is not None:

            mapping[key] = index

            used.add(index)

    # -----------------------------------
    # Pass 2 : every remaining label takes
    # the next free slot, in order of
    # appearance in the video
    # -----------------------------------

    for activity in activities:

        raw = str(activity.get("operator", "") or "").strip()

        key = raw.lower()

        if not key or key in mapping:
            continue

        free = next(
            (
                i
                for i in range(1, MAX_OPERATORS + 1)
                if i not in used
            ),
            MAX_OPERATORS
        )

        mapping[key] = free

        used.add(free)

    # -----------------------------------
    # Apply the mapping
    # -----------------------------------

    for activity in activities:

        raw = str(activity.get("operator", "") or "").strip()

        index = mapping.get(raw.lower(), 1)

        activity["operator_index"] = index

        activity["operator_label"] = raw

        activity["operator"] = operator_name(index)

    return activities


# ============================================================
# INTERVAL HELPERS
# ============================================================

def merge_intervals(intervals):
    """
    Merge overlapping (start, end) spans so time covered by two
    activities at once is only counted once.
    """

    if not intervals:
        return []

    ordered = sorted(intervals)

    merged = [list(ordered[0])]

    for start, end in ordered[1:]:

        if start <= merged[-1][1]:

            merged[-1][1] = max(merged[-1][1], end)

        else:

            merged.append([start, end])

    return [tuple(span) for span in merged]


def covered_seconds(intervals):
    """
    Total wall-clock seconds covered by a set of spans.
    """

    return round(
        sum(
            end - start
            for start, end in merge_intervals(intervals)
        ),
        3
    )


# ============================================================
# OPERATOR CALCULATIONS
# ============================================================

def update_operator_columns(activities):
    """
    Fill Op1-Op5 and WT1-WT5 for EACH PROCESS.
    Each row stores only that process duration.
    """

    for activity in activities:

        index = activity.get(
            "operator_index",
            1
        )

        duration = activity.get(
            "duration",
            0
        )

        activity_type = activity.get(
            "activity_type",
            "Working"
        )

        # ------------------------------------
        # Reset all columns
        # ------------------------------------

        for slot in range(1, MAX_OPERATORS + 1):

            activity[f"op{slot}"] = 0.0

            activity[f"op_wt{slot}"] = 0.0

        # ------------------------------------
        # Working goes to that operator's Op
        # column, everything else to their WT
        # column
        # ------------------------------------

        if activity_type == "Working":

            activity[f"op{index}"] = round(duration, 3)

        else:

            activity[f"op_wt{index}"] = round(duration, 3)

    return activities


# ============================================================
# OPERATOR COUNT
# ============================================================

def detect_operator_count(activities):
    """
    Return how many distinct operators are present in the video,
    derived from each activity's operator index. Clamped to 1..5.
    """

    operators = set()

    for activity in activities:

        index = activity.get("operator_index")

        if index:
            operators.add(int(index))

    count = len(operators)

    if count < 1:
        count = 1

    if count > MAX_OPERATORS:
        count = MAX_OPERATORS

    return count


# ============================================================
# PER OPERATOR ANALYSIS
# ============================================================

def calculate_operator_analysis(activities):
    """
    Build a full time study for EVERY operator seen in the video.

    Each operator gets their own working / waiting / walking / rework
    split, their own observed window, their own idle time and their own
    utilisation - so a two-operator video is reported as two studies,
    not one blended average.

    Must run after calculate_process_metrics() so TOCT / NVA exist.
    """

    grouped = defaultdict(list)

    for activity in activities:

        grouped[
            activity.get("operator_index", 1)
        ].append(activity)

    # --------------------------------------------
    # The study window is SHARED by every operator:
    # first action in the video to last action.
    #
    # Each operator is measured against this same
    # window, so an operator who stops early is
    # charged for the time they were not working -
    # that idle time is what line balancing needs.
    # --------------------------------------------

    all_spans = []

    for activity in activities:

        start = timestamp_to_seconds(
            activity.get("start_timestamp", "00:00:00.000")
        )

        end = timestamp_to_seconds(
            activity.get("end_timestamp", "00:00:00.000")
        )

        if end > start:
            all_spans.append((start, end))

    if all_spans:

        window_start = min(start for start, _ in all_spans)

        window_end = max(end for _, end in all_spans)

        study_window = round(window_end - window_start, 3)

    else:

        study_window = 0.0

    summary = []

    for index in sorted(grouped):

        rows = grouped[index]

        working = 0.0
        waiting = 0.0
        walking = 0.0
        rework = 0.0

        toct = 0.0
        nva = 0.0
        r_nva = 0.0

        intervals = []

        for activity in rows:

            duration = activity.get("duration", 0) or 0

            activity_type = activity.get(
                "activity_type",
                "Working"
            )

            if activity_type == "Working":
                working += duration

            elif activity_type == "Waiting":
                waiting += duration

            elif activity_type == "Walking":
                walking += duration

            elif activity_type == "Rework":
                rework += duration

            toct += activity.get("toct", 0) or 0

            nva += activity.get("nva", 0) or 0

            r_nva += activity.get("r_nva", 0) or 0

            start = timestamp_to_seconds(
                activity.get("start_timestamp", "00:00:00.000")
            )

            end = timestamp_to_seconds(
                activity.get("end_timestamp", "00:00:00.000")
            )

            if end > start:
                intervals.append((start, end))

        # --------------------------------------------
        # This operator's own observed window
        # --------------------------------------------

        if intervals:

            observed = round(
                max(end for _, end in intervals)
                - min(start for start, _ in intervals),
                3
            )

            first_seen = seconds_to_timestamp(
                min(start for start, _ in intervals)
            )

            last_seen = seconds_to_timestamp(
                max(end for _, end in intervals)
            )

        else:

            observed = 0.0

            first_seen = "00:00:00.000"

            last_seen = "00:00:00.000"

        # --------------------------------------------
        # Time in the study window that this operator
        # has NO recorded activity for. Covers gaps
        # between their activities AND the time before
        # they start or after they stop. It is idle
        # time either way.
        # --------------------------------------------

        gap = round(
            max(0.0, study_window - covered_seconds(intervals)),
            3
        )

        idle = round(waiting + gap, 3)

        # --------------------------------------------
        # Utilisation against the shared study window,
        # so operators are directly comparable
        # --------------------------------------------

        if study_window > 0:

            utilisation = round((working / study_window) * 100, 1)

        else:

            utilisation = 0.0

        total_nva = round(waiting + walking + rework + gap, 3)

        accounted = round(working + waiting + walking + rework, 3)

        if accounted > 0:

            va_percent = round((working / accounted) * 100, 1)

        else:

            va_percent = 0.0

        summary.append({

            "operator": operator_name(index),

            "operator_index": index,

            "processes": len(rows),

            "first_seen": first_seen,

            "last_seen": last_seen,

            "study_window_seconds": study_window,

            "observed_time_seconds": observed,

            "working_time": round(working, 3),

            "waiting_time": round(waiting, 3),

            "walking_time": round(walking, 3),

            "rework_time": round(rework, 3),

            "idle_time": idle,

            "unaccounted_idle_time": gap,

            "total_activity_time": accounted,

            "toct": round(toct, 3),

            "nva": round(total_nva, 3),

            "r_nva": round(r_nva, 3),

            "utilisation_percent": utilisation,

            "value_added_percent": va_percent

        })

    return summary


# ============================================================
# PROCESS CALCULATIONS
# ============================================================

def calculate_process_metrics(activities):
    """
    Calculate TOCT, NVA and R-NVA
    for every individual process.
    """

    for activity in activities:

        duration = activity.get("duration", 0)

        activity_type = activity.get(
            "activity_type",
            "Working"
        )

        # ----------------------------------------
        # Reset values
        # ----------------------------------------

        activity["toct"] = 0.0
        activity["nva"] = 0.0
        activity["r_nva"] = 0.0

        # ----------------------------------------
        # Working
        # ----------------------------------------

        if activity_type == "Working":

            activity["toct"] = round(duration,3)

        # ----------------------------------------
        # Waiting
        # ----------------------------------------

        elif activity_type == "Waiting":

            activity["toct"] = round(duration,3)

            activity["nva"] = round(duration,3)

        # ----------------------------------------
        # Walking
        # ----------------------------------------

        elif activity_type == "Walking":

            activity["toct"] = round(duration,3)

            activity["nva"] = round(duration,3)

        # ----------------------------------------
        # Rework
        # ----------------------------------------

        elif activity_type == "Rework":

            activity["toct"] = round(duration,3)

            activity["nva"] = round(duration,3)

            activity["r_nva"] = round(duration,3)

        else:

            activity["toct"] = round(duration,3)

    return activities


# ============================================================
# OVERALL ANALYSIS
# ============================================================

def calculate_overall_analysis(activities, operator_summary=None):

    overall = {

        "total_time_seconds":0,

        "cycle_time_seconds":0,

        "operator_count":1,

        "operator_working_time":0,

        "walking_time":0,

        "operator_waiting_time":0,

        "rework_time":0,

        "operator_idle_time":0,

        "unaccounted_idle_time":0,

        "inspection_time":0,

        "estimated_value_added_time":0,

        "estimated_non_value_added_time":0,

        "average_operator_utilisation_percent":0

    }

    if not activities:

        return overall

    total_working = 0.0
    total_waiting = 0.0
    total_walking = 0.0
    total_rework = 0.0
    total_nva = 0.0

    starts = []
    ends = []

    for activity in activities:

        duration = activity.get(
            "duration",
            0
        )

        starts.append(
            timestamp_to_seconds(
                activity.get("start_timestamp", "00:00:00.000")
            )
        )

        ends.append(
            timestamp_to_seconds(
                activity.get("end_timestamp", "00:00:00.000")
            )
        )

        activity_type = activity.get(
            "activity_type",
            "Working"
        )

        # ----------------------------------------

        if activity_type == "Working":

            total_working += duration

        elif activity_type == "Waiting":

            total_waiting += duration

            total_nva += duration

        elif activity_type == "Walking":

            total_walking += duration

            total_nva += duration

        elif activity_type == "Rework":

            total_rework += duration

            total_nva += duration

    # --------------------------------------------------
    # Total observed time = first start -> last end
    # --------------------------------------------------

    total_time = round(
        max(ends) - min(starts),
        3
    )

    if total_time < 0:

        total_time = 0.0

    # --------------------------------------------------
    # Gap time: seconds inside an operator's own window
    # that were NOT captured as any activity. This is
    # idle time too.
    #
    # It MUST be measured per operator: when two operators
    # work in parallel the sum of their durations can
    # exceed the video length, which would otherwise wipe
    # the gap out to zero.
    # --------------------------------------------------

    if operator_summary is None:

        operator_summary = calculate_operator_analysis(activities)

    gap_time = round(
        sum(
            operator.get("unaccounted_idle_time", 0)
            for operator in operator_summary
        ),
        3
    )

    # --------------------------------------------------
    # Idle time = explicit waiting + uncaptured gaps
    # --------------------------------------------------

    idle_time = round(
        total_waiting + gap_time,
        3
    )

    # --------------------------------------------------
    # Operator headcount and average utilisation
    # --------------------------------------------------

    operator_count = max(len(operator_summary), 1)

    if operator_summary:

        average_utilisation = round(
            sum(
                operator.get("utilisation_percent", 0)
                for operator in operator_summary
            ) / operator_count,
            1
        )

    else:

        average_utilisation = 0.0

    overall["total_time_seconds"] = total_time

    overall["cycle_time_seconds"] = total_time

    overall["operator_count"] = operator_count

    overall["average_operator_utilisation_percent"] = average_utilisation

    overall["operator_working_time"] = round(
        total_working,
        3
    )

    overall["walking_time"] = round(
        total_walking,
        3
    )

    overall["operator_waiting_time"] = round(
        total_waiting,
        3
    )

    overall["rework_time"] = round(
        total_rework,
        3
    )

    overall["operator_idle_time"] = idle_time

    overall["unaccounted_idle_time"] = gap_time

    overall["inspection_time"] = 0.0

    overall["estimated_value_added_time"] = round(
        total_working,
        3
    )

    overall["estimated_non_value_added_time"] = round(
        total_nva,
        3
    )

    return overall
# ============================================================
# MAIN TIME STUDY ENGINE
# ============================================================

def calculate_time_study(data):
    """
    Complete Industrial AI Time Study Engine.

    Workflow:
        1. Validate Gemini output
        2. Calculate Duration
        3. Fill Operator Columns
        4. Calculate TOCT / NVA / R-NVA
        5. Calculate Overall Summary
    """

    # -----------------------------------------
    # Read Activities
    # -----------------------------------------

    activities = data.get("activities", [])

    validated = []

    # -----------------------------------------
    # Validate every activity
    # -----------------------------------------

    for activity in activities:

        validated.append(
            validate_activity(activity)
        )

    # -----------------------------------------
    # Sort chronologically by start timestamp
    # -----------------------------------------

    validated.sort(
        key=lambda a: timestamp_to_seconds(
            a.get("start_timestamp", "00:00:00.000")
        )
    )

    # -----------------------------------------
    # Map every operator label to its own slot
    # -----------------------------------------

    validated = assign_operator_indices(
        validated
    )

    # -----------------------------------------
    # Update Operator Columns
    # -----------------------------------------

    validated = update_operator_columns(
        validated
    )

    # -----------------------------------------
    # Detect Operator Count (1 to 5)
    # -----------------------------------------

    data["operator_count"] = detect_operator_count(
        validated
    )

    # -----------------------------------------
    # Calculate Process Metrics
    # -----------------------------------------

    validated = calculate_process_metrics(
        validated
    )

    # -----------------------------------------
    # Assign NVA Reasons
    # -----------------------------------------

    validated = assign_nva_reasons(
        validated
    )

    # -----------------------------------------
    # Per Operator Time Study
    # -----------------------------------------

    operator_summary = calculate_operator_analysis(
        validated
    )

    # -----------------------------------------
    # Overall Analysis
    # -----------------------------------------

    overall = calculate_overall_analysis(
        validated,
        operator_summary
    )

    # -----------------------------------------
    # Save Results
    # -----------------------------------------

    data["activities"] = validated

    data["operator_analysis"] = operator_summary

    data["overall_analysis"] = overall

    data["total_processes"] = len(validated)

    return data