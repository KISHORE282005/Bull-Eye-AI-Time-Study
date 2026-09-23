# ============================================================
# NVA RULES - THE SEVEN CONDITIONS
# ============================================================
#
# An activity is Non Value Added when it matches ONE of these
# seven conditions. Everything else is productive work.
#
#   1. Excess walking          - more than 5-10 steps
#   2. Searching for tools     - hunting inside the workstation
#   3. Rework                  - repeating or correcting work
#   4. Idle time               - standing idle for over 5 seconds
#   5. Excess movement         - unnecessary motion at the station
#   6. Speaking                - talking instead of working
#   7. Operator not available  - station left unmanned
#
# The two thresholds below are the plant's tuning knobs. Change
# them here and the whole report follows.
# ============================================================

# Idle / waiting longer than this many seconds is NVA.
# A shorter pause is a normal work pause.
IDLE_NVA_THRESHOLD_SECONDS = 5.0

# Walking more than this many steps is NVA.
# A shorter walk inside the workstation is normal work.
WALKING_STEP_THRESHOLD = 5

# Used only when the AI did not count the steps itself.
# A walking operator covers roughly two steps per second.
STEPS_PER_SECOND = 2.0


EXCESS_WALKING = "Excess walking"
SEARCHING_FOR_TOOLS = "Searching for tools"
REWORK = "Rework"
IDLE_TIME = "Idle time"
EXCESS_MOVEMENT = "Excess movement"
SPEAKING = "Speaking"
OPERATOR_NOT_AVAILABLE = "Operator not available"


NVA_CATEGORIES = [
    EXCESS_WALKING,
    SEARCHING_FOR_TOOLS,
    REWORK,
    IDLE_TIME,
    EXCESS_MOVEMENT,
    SPEAKING,
    OPERATOR_NOT_AVAILABLE
]


# What each category means, printed in the Excel report so the
# reader knows why the time was counted against them.
NVA_CATEGORY_DEFINITIONS = {

    EXCESS_WALKING:
        f"Operator walked more than {WALKING_STEP_THRESHOLD}-10 steps to reach a part, "
        "tool, rack or another workstation.",

    SEARCHING_FOR_TOOLS:
        "Operator searched for a tool, fastener or material inside the workstation.",

    REWORK:
        "Operator repeated or corrected work that was already completed.",

    IDLE_TIME:
        f"Operator stood idle, waited or watched for more than "
        f"{IDLE_NVA_THRESHOLD_SECONDS:.0f} seconds.",

    EXCESS_MOVEMENT:
        "Unnecessary motion at the workstation - over-reaching, bending, twisting or "
        "re-gripping the same part.",

    SPEAKING:
        "Operator was talking, being instructed or on the phone instead of working.",

    OPERATOR_NOT_AVAILABLE:
        "Operator left the workstation and the station stood unmanned."

}


# Keywords that identify each condition from the AI's own wording.
# Order matters - the most specific condition is tested first.
CATEGORY_KEYWORD_RULES = [

    # 7. Operator not available
    # Kept narrow on purpose: "tool not available" is a SEARCHING
    # problem, not an absent operator.
    (OPERATOR_NOT_AVAILABLE, [
        "operator not available", "operator is not available", "man not available",
        "operator unavailable", "left the workstation", "leaves the workstation",
        "away from the workstation", "operator absent", "operator is absent",
        "out of frame", "unmanned", "station empty", "operator missing",
        "not at the workstation", "left the station", "no operator at"
    ]),

    # 3. Rework
    # "fixing the bracket" and "tightens it again" are normal assembly,
    # so only unambiguous repeat-work wording is listed.
    (REWORK, [
        "rework", "re-work", "redo", "re-do", "do it again", "does it again",
        "repeat tightening", "repeat assembly", "repeat inspection", "repeat work",
        "repeats the", "re-align", "realign", "re-weld", "reweld", "grind back",
        "grinds back", "defect", "had to correct", "corrects the earlier",
        "already completed", "was not correct", "second attempt"
    ]),

    # 6. Speaking
    (SPEAKING, [
        "talking", "talks", "speaking", "speaks", "conversation", "discussing",
        "discussion", "discusses", "chatting", "chat", "instructed", "instruction from",
        "asking", "asks a colleague", "phone", "mobile", "briefing", "explaining"
    ]),

    # 2. Searching for tools
    (SEARCHING_FOR_TOOLS, [
        "searching", "searches", "search", "looking for", "looks for", "hunting",
        "rummag", "find the tool", "finding the tool", "locate the tool",
        "tool not available", "tool missing", "checking the bin", "checks the bin",
        "opening bins", "scanning the bench", "pockets", "cannot find", "can not find"
    ]),

    # 1. Excess walking
    (EXCESS_WALKING, [
        "walking", "walks", "walked", "steps across", "crosses the bay",
        "travels to", "goes to the rack", "goes to the bin", "trolley trip",
        "back and forth", "repeated trips", "fetch", "fetches"
    ]),

    # 5. Excess movement
    # Climbing and bending are often unavoidable on a machine this
    # size, so only wording that calls the motion wasteful is listed.
    (EXCESS_MOVEMENT, [
        "over-reach", "overreach", "over reach", "excess motion",
        "excessive motion", "unnecessary motion", "unnecessary movement",
        "excess movement", "excessive movement", "repeated bending",
        "repeatedly bends", "re-grip", "regrip", "shifts the part again",
        "awkward posture", "awkward reach", "strains to reach"
    ]),

    # 4. Idle time
    (IDLE_TIME, [
        "idle", "waiting", "waits", "stands by", "standing by", "stood by",
        "watching", "watches", "does nothing", "doing nothing", "pause", "delay",
        "holds up", "held up", "stalled"
    ])

]


# Each NVA cause rolls up into one of the seven conditions, so a
# reason supplied by the AI always lands in the right bucket.
REASON_TO_CATEGORY = {

    "Excessive walking": EXCESS_WALKING,
    "Material stored far from the workstation": EXCESS_WALKING,
    "Excess transportation": EXCESS_WALKING,
    "Repeated trips to collect materials": EXCESS_WALKING,

    "Worker searching for tools or materials": SEARCHING_FOR_TOOLS,
    "Tool not available nearby": SEARCHING_FOR_TOOLS,
    "Tool change delay": SEARCHING_FOR_TOOLS,
    "Bolt, nut, or component located away from the operator": SEARCHING_FOR_TOOLS,
    "Missing components": SEARCHING_FOR_TOOLS,
    "Poor 5S implementation": SEARCHING_FOR_TOOLS,

    "Rework": REWORK,
    "Incorrect material placement": REWORK,

    "Waiting for material availability": IDLE_TIME,
    "Waiting for machine completion": IDLE_TIME,
    "Waiting for another operator": IDLE_TIME,
    "Waiting for supervisor approval": IDLE_TIME,
    "Quality inspection waiting": IDLE_TIME,
    "Machine downtime": IDLE_TIME,
    "Equipment malfunction": IDLE_TIME,
    "Material replenishment delay": IDLE_TIME,
    "Inventory shortage": IDLE_TIME,
    "Conveyor delay": IDLE_TIME,
    "Safety clearance delay": IDLE_TIME,
    "Congestion in work area": IDLE_TIME,
    "Forklift traffic": IDLE_TIME,
    "Operator idle for more than 5 seconds": IDLE_TIME,

    "Unnecessary motion": EXCESS_MOVEMENT,
    "Poor ergonomics": EXCESS_MOVEMENT,
    "Poor workstation layout": EXCESS_MOVEMENT,
    "Inefficient workflow": EXCESS_MOVEMENT,
    "Lack of standardization": EXCESS_MOVEMENT,
    "Excess body movement at the workstation": EXCESS_MOVEMENT,

    "Communication delay": SPEAKING,
    "Operator confusion": SPEAKING,
    "Poor work instructions": SPEAKING,
    "Talking or discussion instead of working": SPEAKING,

    "Operator not available at the workstation": OPERATOR_NOT_AVAILABLE

}


# The cause written into the report when a condition was detected
# from the video but the AI gave no usable reason of its own.
CATEGORY_DEFAULT_REASON = {

    EXCESS_WALKING: "Excessive walking",
    SEARCHING_FOR_TOOLS: "Worker searching for tools or materials",
    REWORK: "Rework",
    IDLE_TIME: "Operator idle for more than 5 seconds",
    EXCESS_MOVEMENT: "Excess body movement at the workstation",
    SPEAKING: "Talking or discussion instead of working",
    OPERATOR_NOT_AVAILABLE: "Operator not available at the workstation"

}


# ============================================================
# NVA CAUSES
# ============================================================

NVA_CAUSES = [
    "Excessive walking",
    "Material stored far from the workstation",
    "Bolt, nut, or component located away from the operator",
    "Worker searching for tools or materials",
    "Waiting for material availability",
    "Waiting for machine completion",
    "Waiting for another operator",
    "Waiting for supervisor approval",
    "Machine downtime",
    "Poor workstation layout",
    "Poor ergonomics",
    "Excess transportation",
    "Unnecessary motion",
    "Repeated trips to collect materials",
    "Material replenishment delay",
    "Incorrect material placement",
    "Inventory shortage",
    "Tool not available nearby",
    "Tool change delay",
    "Quality inspection waiting",
    "Rework",
    "Congestion in work area",
    "Forklift traffic",
    "Conveyor delay",
    "Operator confusion",
    "Missing components",
    "Poor work instructions",
    "Inefficient workflow",
    "Lack of standardization",
    "Poor 5S implementation",
    "Safety clearance delay",
    "Equipment malfunction",
    "Communication delay",
    "Operator not available at the workstation",
    "Operator idle for more than 5 seconds",
    "Excess body movement at the workstation",
    "Talking or discussion instead of working"
]

# ============================================================
# KEYWORD -> NVA REASON
# ============================================================

KEYWORD_RULES = [
    ("rework", "Rework"),
    ("re-do", "Rework"),
    ("redo", "Rework"),
    ("repeat tightening", "Rework"),
    ("repeat assembly", "Rework"),
    ("repeat inspection", "Rework"),
    ("repeat work", "Rework"),
    ("do it again", "Rework"),
    ("correct", "Rework"),
    ("reposition part", "Rework"),
    ("repeat", "Rework"),
    ("machine downtime", "Machine downtime"),
    ("machine delay", "Machine downtime"),
    ("equipment malfunction", "Equipment malfunction"),
    ("equipment failure", "Equipment malfunction"),
    ("breakdown", "Equipment malfunction"),
    ("machine failure", "Equipment malfunction"),
    ("machine completion", "Waiting for machine completion"),
    ("waiting for machine", "Waiting for machine completion"),
    ("waiting for machin", "Waiting for machine completion"),
    ("machin", "Waiting for machine completion"),
    ("cnc", "Waiting for machine completion"),
    ("cycle complete", "Waiting for machine completion"),
    ("waiting for material", "Waiting for material availability"),
    ("material delay", "Waiting for material availability"),
    ("material availability", "Waiting for material availability"),
    ("waiting for part", "Waiting for material availability"),
    ("part not arrived", "Waiting for material availability"),
    ("material replenishment", "Material replenishment delay"),
    ("replenish", "Material replenishment delay"),
    ("restock", "Material replenishment delay"),
    ("refill", "Material replenishment delay"),
    ("inventory shortage", "Inventory shortage"),
    ("shortage", "Inventory shortage"),
    ("out of stock", "Inventory shortage"),
    ("ran out", "Inventory shortage"),
    ("missing component", "Missing components"),
    ("missing part", "Missing components"),
    ("component missing", "Missing components"),
    ("part missing", "Missing components"),
    ("waiting for another operator", "Waiting for another operator"),
    ("waiting for other operator", "Waiting for another operator"),
    ("waiting for co-worker", "Waiting for another operator"),
    ("waiting for assistant", "Waiting for another operator"),
    ("waiting for colleague", "Waiting for another operator"),
    ("waiting for help", "Waiting for another operator"),
    ("waiting for supervisor", "Waiting for supervisor approval"),
    ("supervisor approval", "Waiting for supervisor approval"),
    ("manager approval", "Waiting for supervisor approval"),
    ("sign off", "Waiting for supervisor approval"),
    ("quality inspection", "Quality inspection waiting"),
    ("waiting for quality", "Quality inspection waiting"),
    ("waiting for inspector", "Quality inspection waiting"),
    ("waiting for qc", "Quality inspection waiting"),
    ("waiting for qa", "Quality inspection waiting"),
    ("tool not available", "Tool not available nearby"),
    ("tool missing", "Tool not available nearby"),
    ("searching tool", "Tool not available nearby"),
    ("looking for tool", "Tool not available nearby"),
    ("find tool", "Tool not available nearby"),
    ("tool search", "Tool not available nearby"),
    ("tool change", "Tool change delay"),
    ("change tool", "Tool change delay"),
    ("changing tool", "Tool change delay"),
    ("tool replacement", "Tool change delay"),
    ("swapping tool", "Tool change delay"),
    ("searching", "Worker searching for tools or materials"),
    ("looking for", "Worker searching for tools or materials"),
    ("search", "Worker searching for tools or materials"),
    ("looking", "Worker searching for tools or materials"),
    ("search for", "Worker searching for tools or materials"),
    ("find material", "Worker searching for tools or materials"),
    ("conveyor", "Conveyor delay"),
    ("forklift", "Forklift traffic"),
    ("fork lift", "Forklift traffic"),
    ("fork-lift", "Forklift traffic"),
    ("congestion", "Congestion in work area"),
    ("crowded", "Congestion in work area"),
    ("blocked", "Congestion in work area"),
    ("blocking", "Congestion in work area"),
    ("obstruction", "Congestion in work area"),
    ("traffic", "Congestion in work area"),
    ("communication", "Communication delay"),
    ("asking", "Communication delay"),
    ("talking", "Communication delay"),
    ("conversation", "Communication delay"),
    ("discuss", "Communication delay"),
    ("safety", "Safety clearance delay"),
    ("clearance", "Safety clearance delay"),
    ("guard", "Safety clearance delay"),
    ("permit", "Safety clearance delay"),
    ("confusion", "Operator confusion"),
    ("confused", "Operator confusion"),
    ("uncertain", "Operator confusion"),
    ("hesitat", "Operator confusion"),
    ("checking drawing", "Operator confusion"),
    ("instruction", "Poor work instructions"),
    ("drawing", "Poor work instructions"),
    ("document", "Poor work instructions"),
    ("manual", "Poor work instructions"),
    ("procedure", "Poor work instructions"),
    ("standardiz", "Lack of standardization"),
    ("non-standard", "Lack of standardization"),
    ("inconsistent", "Lack of standardization"),
    ("5s", "Poor 5S implementation"),
    ("5 s", "Poor 5S implementation"),
    ("housekeeping", "Poor 5S implementation"),
    ("clutter", "Poor 5S implementation"),
    ("disorganized", "Poor 5S implementation"),
    ("untidy", "Poor 5S implementation"),
    ("messy", "Poor 5S implementation"),
    ("clean", "Poor 5S implementation"),
    ("inefficient", "Inefficient workflow"),
    ("workflow", "Inefficient workflow"),
    ("repetitive", "Inefficient workflow"),
    ("incorrect material placement", "Incorrect material placement"),
    ("misplaced", "Incorrect material placement"),
    ("wrong position", "Incorrect material placement"),
    ("misplacement", "Incorrect material placement"),
    ("re-position", "Incorrect material placement"),
    ("excess transportation", "Excess transportation"),
    ("transportation", "Excess transportation"),
    ("transport", "Excess transportation"),
    ("trolley", "Excess transportation"),
    ("cart", "Excess transportation"),
    ("unnecessary motion", "Unnecessary motion"),
    ("unnecessary movement", "Unnecessary motion"),
    ("excess motion", "Unnecessary motion"),
    ("extra reach", "Unnecessary motion"),
    ("reach", "Unnecessary motion"),
    ("stretch", "Unnecessary motion"),
    ("repeated trips", "Repeated trips to collect materials"),
    ("repeated trip", "Repeated trips to collect materials"),
    ("collect material", "Repeated trips to collect materials"),
    ("collecting material", "Repeated trips to collect materials"),
    ("collect part", "Repeated trips to collect materials"),
    ("fetch", "Repeated trips to collect materials"),
    ("back and forth", "Repeated trips to collect materials"),
    ("stored far", "Material stored far from the workstation"),
    ("far from", "Material stored far from the workstation"),
    ("distant", "Material stored far from the workstation"),
    ("storage", "Material stored far from the workstation"),
    ("remote rack", "Material stored far from the workstation"),
    ("far away", "Material stored far from the workstation"),
    ("bolt", "Bolt, nut, or component located away from the operator"),
    ("nut", "Bolt, nut, or component located away from the operator"),
    ("component located", "Bolt, nut, or component located away from the operator"),
    ("hardware", "Bolt, nut, or component located away from the operator"),
    ("located away", "Bolt, nut, or component located away from the operator"),
    ("rack", "Bolt, nut, or component located away from the operator"),
    ("bin", "Bolt, nut, or component located away from the operator"),
    ("shelf", "Bolt, nut, or component located away from the operator"),
    ("layout", "Poor workstation layout"),
    ("workstation arrangement", "Poor workstation layout"),
    ("workstation design", "Poor workstation layout"),
    ("ergonom", "Poor ergonomics"),
    ("posture", "Poor ergonomics"),
    ("bend", "Poor ergonomics"),
    ("awkward", "Poor ergonomics"),
    ("excessive walking", "Excessive walking"),
    ("walking", "Excessive walking"),
    ("walk", "Excessive walking")
]

# ============================================================
# NVA CATEGORY - THE SEVEN CONDITIONS
# ============================================================

def activity_text(activity):
    """
    What the AI observed in the video, lower-cased, so the seven
    conditions can be matched against it.

    `nva_reason` is deliberately left out: it is a generic label and
    is rolled up separately. Mixing it in here would read a cause like
    "Tool not available nearby" as an absent operator.
    """

    return " ".join(
        str(activity.get(key, "") or "")
        for key in [
            "process_name",
            "process_operation",
            "process_description"
        ]
    ).lower()


def estimated_steps(activity):
    """
    How many steps the operator took during a walking activity.

    The AI is asked to count them. When it does not, fall back to the
    duration: a walking operator covers about two steps per second.
    """

    try:
        steps = int(float(activity.get("walking_steps", 0) or 0))
    except (TypeError, ValueError):
        steps = 0

    if steps > 0:
        return steps

    duration = activity.get("duration", 0) or 0

    return int(round(duration * STEPS_PER_SECOND))


def assign_nva_category(activity):
    """
    Decide which of the seven NVA conditions an activity falls under.

    Returns "" when the activity is productive work - including a short
    walk of 5 steps or fewer and a short pause of 5 seconds or less,
    which are normal work and must never be charged as NVA.
    """

    from utils.calculations import classify_activity

    activity_type = activity.get(
        "activity_type",
        classify_activity(
            activity.get("process_operation", "")
        )
    )

    duration = activity.get("duration", 0) or 0

    text = activity_text(activity)

    # --------------------------------------------------------
    # 1. Trust a valid category the AI already supplied
    # --------------------------------------------------------

    supplied = str(
        activity.get("nva_category", "") or ""
    ).strip()

    for category in NVA_CATEGORIES:

        if supplied.lower() == category.lower():

            # The two thresholds still overrule the AI: a short walk
            # or a short pause is normal work however it was tagged.

            if category == EXCESS_WALKING:

                if estimated_steps(activity) <= WALKING_STEP_THRESHOLD:
                    return ""

            if category == IDLE_TIME:

                if duration <= IDLE_NVA_THRESHOLD_SECONDS:
                    return ""

            return category

    # --------------------------------------------------------
    # 2. Read the condition out of what was actually observed.
    #
    # This runs BEFORE the reason rollup: an operator described as
    # "standing and discussing" is Speaking even when the AI labelled
    # the cause generically as a material wait.
    # --------------------------------------------------------

    category = None

    for candidate, keywords in CATEGORY_KEYWORD_RULES:

        if any(keyword in text for keyword in keywords):

            category = candidate

            break

    # --------------------------------------------------------
    # 3. Otherwise roll the AI's cause up into its condition
    # --------------------------------------------------------

    if not category:

        reason = str(
            activity.get("nva_reason", "") or ""
        ).strip()

        category = REASON_TO_CATEGORY.get(reason)

    # --------------------------------------------------------
    # 4. Fall back to the operation type
    # --------------------------------------------------------

    if not category:

        if activity_type == "Rework":
            category = REWORK

        elif activity_type == "Walking":
            category = EXCESS_WALKING

        elif activity_type == "Waiting":
            category = IDLE_TIME

    if not category:
        return ""

    # --------------------------------------------------------
    # 5. Apply the two thresholds
    # --------------------------------------------------------

    if category == EXCESS_WALKING:

        # A walk of 5 steps or fewer stays inside the workstation
        # and is part of the job, not a loss.

        if estimated_steps(activity) <= WALKING_STEP_THRESHOLD:
            return ""

    if category == IDLE_TIME:

        # A pause of 5 seconds or less is a normal work pause.

        if duration <= IDLE_NVA_THRESHOLD_SECONDS:
            return ""

    # --------------------------------------------------------
    # 6. Productive work is only NVA when the motion itself is
    #    the waste - searching, talking, rework, excess movement
    # --------------------------------------------------------

    if activity_type == "Working":

        if category in (EXCESS_WALKING, IDLE_TIME, OPERATOR_NOT_AVAILABLE):
            return ""

    return category


def assign_nva_categories(activities):
    """
    Tag every activity with its NVA condition and mark whether it is
    Non Value Added. Runs before the TOCT / NVA maths so the seven
    conditions decide what gets charged as NVA.
    """

    for activity in activities:

        category = assign_nva_category(activity)

        activity["nva_category"] = category

        activity["is_nva"] = bool(category)

        activity["walking_steps"] = (
            estimated_steps(activity)
            if activity.get("activity_type") == "Walking"
            else 0
        )

    return activities


# ============================================================
# ASSIGN NVA REASON
# ============================================================

def assign_nva_reason(activity):
    """
    Pick the most specific NVA cause for a non-value-added activity
    using keyword matching over process_name / process_operation /
    process_description. Returns '' for value-added activities.

    Runs after assign_nva_categories(), so an activity is only given a
    cause when one of the seven conditions actually flagged it.
    """

    category = str(
        activity.get("nva_category", "") or ""
    ).strip()

    if not category:
        return ""

    existing = str(
        activity.get("nva_reason", "")
    ).strip()

    # Keep the AI's own cause when it is on the list AND it agrees
    # with the condition that was detected, so the two columns can
    # never contradict each other.

    if existing in NVA_CAUSES:

        if REASON_TO_CATEGORY.get(existing, category) == category:
            return existing

    # Build searchable text
    text = " ".join(
        str(activity.get(key, ""))
        for key in [
            "process_name",
            "process_operation",
            "process_description"
        ]
    ).lower()

    for keyword, reason in KEYWORD_RULES:

        if keyword in text:

            if REASON_TO_CATEGORY.get(reason) == category:
                return reason

    return CATEGORY_DEFAULT_REASON.get(category, "")


# ============================================================
# ASSIGN ALL REASONS
# ============================================================

def assign_nva_reasons(activities):
    """
    Fill the nva_reason column for every activity.
    Existing valid reasons from Gemini are kept.
    """

    for activity in activities:

        activity.setdefault("nva_reason", "")

        reason = assign_nva_reason(activity)

        if reason:
            activity["nva_reason"] = reason

        else:

            activity["nva_reason"] = ""

    return activities
