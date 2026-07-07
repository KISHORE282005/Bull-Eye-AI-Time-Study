from datetime import datetime
from collections import defaultdict


# ============================================================
# TIME FUNCTIONS
# ============================================================

def time_to_seconds(time_string):
    """
    Convert HH:MM:SS.xx into seconds
    """

    if not time_string:
        return 0.0

    try:

        if "." in time_string:

            t = datetime.strptime(
                time_string,
                "%H:%M:%S.%f"
            )

        else:

            t = datetime.strptime(
                time_string,
                "%H:%M:%S"
            )

        return (
            t.hour * 3600 +
            t.minute * 60 +
            t.second +
            t.microsecond / 1000000
        )

    except Exception:

        return 0.0


# ============================================================
# SECONDS TO TIME
# ============================================================

def seconds_to_time(seconds):

    if seconds < 0:
        seconds = 0

    hours = int(seconds // 3600)

    seconds %= 3600

    minutes = int(seconds // 60)

    seconds %= 60

    return f"{hours:02}:{minutes:02}:{seconds:05.2f}"


# ============================================================
# DURATION
# ============================================================

def calculate_duration(start_time, end_time):

    start = time_to_seconds(start_time)

    end = time_to_seconds(end_time)

    duration = round(end - start, 2)

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

    "Walking to Machine"

]


REWORK = [

    "Rework",

    "Repeat Inspection",

    "Repeat Tightening",

    "Repeat Assembly"

]


# ============================================================
# ACTIVITY TYPE
# ============================================================

def classify_activity(activity_name):

    if not activity_name:
        return "Unknown"

    activity_name = activity_name.lower()

    for item in WORKING:

        if item.lower() in activity_name:
            return "Working"

    for item in WAITING:

        if item.lower() in activity_name:
            return "Waiting"

    for item in WALKING:

        if item.lower() in activity_name:
            return "Walking"

    for item in REWORK:

        if item.lower() in activity_name:
            return "Rework"

    return "Working"


# ============================================================
# VALIDATE ACTIVITY
# ============================================================

def validate_activity(activity):

    start = activity.get("start_time", "00:00:00")

    end = activity.get("end_time", "00:00:00")

    duration = calculate_duration(start, end)

    activity["duration"] = duration

    activity["activity_type"] = classify_activity(

        activity.get(

            "process_operation",

            ""

        )

    )

    return activity
# ============================================================
# OPERATOR CALCULATIONS
# ============================================================

def calculate_operator_times(activities):
    """
    Calculate operator working time and waiting time.
    """

    operator_work = defaultdict(float)
    operator_wait = defaultdict(float)

    for activity in activities:

        activity = validate_activity(activity)

        operator = activity.get(
            "operator",
            "Operator 1"
        )

        duration = activity["duration"]

        activity_type = activity["activity_type"]

        # -----------------------------
        # Working Activities
        # -----------------------------

        if activity_type == "Working":

            operator_work[operator] += duration

        # -----------------------------
        # Waiting Activities
        # -----------------------------

        elif activity_type in [

            "Waiting",

            "Walking",

            "Rework"

        ]:

            operator_wait[operator] += duration

    return operator_work, operator_wait


# ============================================================
# UPDATE OPERATOR COLUMNS
# ============================================================

def update_operator_columns(activities):

    operator_work, operator_wait = calculate_operator_times(
        activities
    )

    for activity in activities:

        operator = activity.get(
            "operator",
            "Operator 1"
        )

        # ---------------------------------
        # Reset Columns
        # ---------------------------------

        activity["op1"] = 0
        activity["op2"] = 0
        activity["op3"] = 0
        activity["op4"] = 0
        activity["op5"] = 0

        activity["op_wt1"] = 0
        activity["op_wt2"] = 0
        activity["op_wt3"] = 0
        activity["op_wt4"] = 0
        activity["op_wt5"] = 0

        # ---------------------------------
        # Operator 1
        # ---------------------------------

        if operator == "Operator 1":

            activity["op1"] = round(
                operator_work["Operator 1"],
                2
            )

            activity["op_wt1"] = round(
                operator_wait["Operator 1"],
                2
            )

        # ---------------------------------
        # Operator 2
        # ---------------------------------

        elif operator == "Operator 2":

            activity["op2"] = round(
                operator_work["Operator 2"],
                2
            )

            activity["op_wt2"] = round(
                operator_wait["Operator 2"],
                2
            )

        # ---------------------------------
        # Operator 3
        # ---------------------------------

        elif operator == "Operator 3":

            activity["op3"] = round(
                operator_work["Operator 3"],
                2
            )

            activity["op_wt3"] = round(
                operator_wait["Operator 3"],
                2
            )

        # ---------------------------------
        # Operator 4
        # ---------------------------------

        elif operator == "Operator 4":

            activity["op4"] = round(
                operator_work["Operator 4"],
                2
            )

            activity["op_wt4"] = round(
                operator_wait["Operator 4"],
                2
            )

        # ---------------------------------
        # Operator 5
        # ---------------------------------

        elif operator == "Operator 5":

            activity["op5"] = round(
                operator_work["Operator 5"],
                2
            )

            activity["op_wt5"] = round(
                operator_wait["Operator 5"],
                2
            )

    return activities
# ============================================================
# PROCESS CALCULATIONS
# ============================================================

def calculate_process_metrics(activities):
    """
    Calculate TOCT, NVA and R-NVA for each activity row.
    """

    for activity in activities:

        activity = validate_activity(activity)

        duration = activity["duration"]

        activity_type = activity["activity_type"]

        # ------------------------------------
        # Reset values
        # ------------------------------------

        activity["toct"] = 0.0
        activity["nva"] = 0.0
        activity["r_nva"] = 0.0

        # ------------------------------------
        # Working Activity
        # ------------------------------------

        if activity_type == "Working":

            activity["toct"] = round(duration, 2)

            activity["nva"] = 0.0

            activity["r_nva"] = 0.0

        # ------------------------------------
        # Waiting
        # ------------------------------------

        elif activity_type == "Waiting":

            activity["toct"] = round(duration, 2)

            activity["nva"] = round(duration, 2)

            activity["r_nva"] = 0.0

        # ------------------------------------
        # Walking
        # ------------------------------------

        elif activity_type == "Walking":

            activity["toct"] = round(duration, 2)

            activity["nva"] = round(duration, 2)

            activity["r_nva"] = 0.0

        # ------------------------------------
        # Rework
        # ------------------------------------

        elif activity_type == "Rework":

            activity["toct"] = round(duration, 2)

            activity["nva"] = round(duration, 2)

            activity["r_nva"] = round(duration, 2)

        else:

            activity["toct"] = round(duration, 2)

    return activities


# ============================================================
# OVERALL ANALYSIS
# ============================================================

def calculate_overall_analysis(activities):

    overall = {

        "cycle_time_seconds": 0,

        "operator_working_time": 0,

        "walking_time": 0,

        "operator_idle_time": 0,

        "inspection_time": 0,

        "estimated_value_added_time": 0,

        "estimated_non_value_added_time": 0

    }

    total_cycle = 0

    total_working = 0

    total_walking = 0

    total_waiting = 0

    total_nva = 0

    for activity in activities:

        duration = activity["duration"]

        total_cycle += duration

        if activity["activity_type"] == "Working":

            total_working += duration

        elif activity["activity_type"] == "Walking":

            total_walking += duration

            total_nva += duration

        elif activity["activity_type"] == "Waiting":

            total_waiting += duration

            total_nva += duration

        elif activity["activity_type"] == "Rework":

            total_nva += duration

    overall["cycle_time_seconds"] = round(total_cycle,2)

    overall["operator_working_time"] = round(total_working,2)

    overall["walking_time"] = round(total_walking,2)

    overall["operator_idle_time"] = round(total_waiting,2)

    overall["estimated_value_added_time"] = round(total_working,2)

    overall["estimated_non_value_added_time"] = round(total_nva,2)

    return overall


# ============================================================
# MAIN ENGINE
# ============================================================

def calculate_time_study(data):

    activities = data["activities"]

    # Validate activities
    activities = [
        validate_activity(a)
        for a in activities
    ]

    # Fill Op1-WT5
    activities = update_operator_columns(
        activities
    )

    # Fill TOCT/NVA/R-NVA
    activities = calculate_process_metrics(
        activities
    )

    # Overall Summary
    overall = calculate_overall_analysis(
        activities
    )

    data["activities"] = activities

    data["overall_analysis"] = overall

    data["total_processes"] = len(activities)

    return data