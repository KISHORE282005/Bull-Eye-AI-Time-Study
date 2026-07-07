from datetime import datetime


# ==========================================
# TIME FUNCTIONS
# ==========================================

def time_to_seconds(time_str):
    """
    Converts HH:MM:SS into seconds.
    """

    try:
        t = datetime.strptime(time_str, "%H:%M:%S")
        return t.hour * 3600 + t.minute * 60 + t.second
    except:
        return 0


def calculate_duration(start_time, end_time):
    """
    Duration = End - Start
    """

    start = time_to_seconds(start_time)
    end = time_to_seconds(end_time)

    return max(0, end - start)


# ==========================================
# OPERATOR TIMES
# ==========================================

def calculate_working_time(activity_type, duration):
    """
    Working activities.
    """

    working = [
        "working",
        "assembly",
        "welding",
        "inspection",
        "machine_loading",
        "machine_unloading",
        "tool_change"
    ]

    if activity_type.lower() in working:
        return duration

    return 0


def calculate_waiting_time(activity_type, duration):
    """
    Waiting / Idle activities.
    """

    waiting = [
        "waiting",
        "idle"
    ]

    if activity_type.lower() in waiting:
        return duration

    return 0


# ==========================================
# NVA
# ==========================================

def calculate_nva(activity_type, duration):
    """
    Non Value Added Time
    """

    nva = [
        "walking",
        "waiting",
        "searching",
        "transport",
        "idle"
    ]

    if activity_type.lower() in nva:
        return duration

    return 0


# ==========================================
# R-NVA
# ==========================================

def calculate_rnva(activity_type, duration):
    """
    Repeat Non Value Added
    """

    if activity_type.lower() == "rework":
        return duration

    return 0


# ==========================================
# TOCT
# ==========================================

def calculate_toct(duration):
    """
    Total Operation Cycle Time
    """

    return duration