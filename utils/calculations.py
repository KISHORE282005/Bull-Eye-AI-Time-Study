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

    activity.setdefault("operator", "Operator 1")

    return activity
# ============================================================
# OPERATOR CALCULATIONS
# ============================================================

def update_operator_columns(activities):
    """
    Fill Op1-Op5 and WT1-WT5 for EACH PROCESS.
    Each row stores only that process duration.
    """

    for activity in activities:

        operator = activity.get(
            "operator",
            "Operator 1"
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

        activity["op1"] = 0.0
        activity["op2"] = 0.0
        activity["op3"] = 0.0
        activity["op4"] = 0.0
        activity["op5"] = 0.0

        activity["op_wt1"] = 0.0
        activity["op_wt2"] = 0.0
        activity["op_wt3"] = 0.0
        activity["op_wt4"] = 0.0
        activity["op_wt5"] = 0.0

        # ------------------------------------
        # Working Time
        # ------------------------------------

        if activity_type == "Working":

            if operator == "Operator 1":
                activity["op1"] = round(duration, 3)

            elif operator == "Operator 2":
                activity["op2"] = round(duration, 3)

            elif operator == "Operator 3":
                activity["op3"] = round(duration, 3)

            elif operator == "Operator 4":
                activity["op4"] = round(duration, 3)

            elif operator == "Operator 5":
                activity["op5"] = round(duration, 3)

        # ------------------------------------
        # Waiting / Walking / Rework
        # ------------------------------------

        else:

            if operator == "Operator 1":
                activity["op_wt1"] = round(duration, 3)

            elif operator == "Operator 2":
                activity["op_wt2"] = round(duration, 3)

            elif operator == "Operator 3":
                activity["op_wt3"] = round(duration, 3)

            elif operator == "Operator 4":
                activity["op_wt4"] = round(duration, 3)

            elif operator == "Operator 5":
                activity["op_wt5"] = round(duration, 3)

    return activities
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

def calculate_overall_analysis(activities):

    overall = {

        "total_time_seconds":0,

        "cycle_time_seconds":0,

        "operator_working_time":0,

        "walking_time":0,

        "operator_waiting_time":0,

        "rework_time":0,

        "operator_idle_time":0,

        "unaccounted_idle_time":0,

        "inspection_time":0,

        "estimated_value_added_time":0,

        "estimated_non_value_added_time":0

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
    # Sum of every activity duration
    # --------------------------------------------------

    sum_durations = round(
        total_working + total_waiting + total_walking + total_rework,
        3
    )

    # --------------------------------------------------
    # Gap time: seconds between activities that were NOT
    # captured as any activity. This is idle time too.
    # --------------------------------------------------

    gap_time = round(
        max(0.0, total_time - sum_durations),
        3
    )

    # --------------------------------------------------
    # Idle time = explicit waiting + uncaptured gaps
    # --------------------------------------------------

    idle_time = round(
        total_waiting + gap_time,
        3
    )

    overall["total_time_seconds"] = total_time

    overall["cycle_time_seconds"] = total_time

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
    # Update Operator Columns
    # -----------------------------------------

    validated = update_operator_columns(
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
    # Overall Analysis
    # -----------------------------------------

    overall = calculate_overall_analysis(
        validated
    )

    # -----------------------------------------
    # Save Results
    # -----------------------------------------

    data["activities"] = validated

    data["overall_analysis"] = overall

    data["total_processes"] = len(validated)

    return data