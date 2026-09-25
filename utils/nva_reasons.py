# ============================================================
# NVA RULES - THE EIGHT CONDITIONS
# ============================================================
#
# An activity is Non Value Added when it matches ONE of these
# eight conditions. Everything else is productive work.
#
#   1. Excess walking          - more than 5-10 steps
#   2. Searching for tools     - tools, materials, documents / drawings
#   3. Rework                  - repeating or correcting work
#   4. Idle time               - idle or waiting for over 5 seconds
#   5. Excess movement         - taking / moving fixtures and templates
#   6. Speaking                - talking or using a mobile phone
#   7. Operator not available  - worker not in the station
#   8. Non-productive task     - PPE, torch cleaning, refills, measuring
#
# Each condition is broken down into the plant's NVA list
# (NVA_CAUSES below), which is what the report shows as the reason.
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
NON_PRODUCTIVE_TASK = "Non-productive task"


NVA_CATEGORIES = [
    EXCESS_WALKING,
    SEARCHING_FOR_TOOLS,
    REWORK,
    IDLE_TIME,
    EXCESS_MOVEMENT,
    SPEAKING,
    OPERATOR_NOT_AVAILABLE,
    NON_PRODUCTIVE_TASK
]


# What each category means, printed in the Excel report so the
# reader knows why the time was counted against them.
NVA_CATEGORY_DEFINITIONS = {

    EXCESS_WALKING:
        f"Operator walked more than {WALKING_STEP_THRESHOLD}-10 steps to reach a part, "
        "tool, rack or another workstation.",

    SEARCHING_FOR_TOOLS:
        "Operator searched for tools, materials, documents or drawing files.",

    REWORK:
        "Operator repeated or corrected work that was already completed.",

    IDLE_TIME:
        f"Operator stood idle or waited for tools, materials, the crane or co-workers "
        f"for more than {IDLE_NVA_THRESHOLD_SECONDS:.0f} seconds.",

    EXCESS_MOVEMENT:
        "Operator took or moved a fixture or template instead of working on the part.",

    SPEAKING:
        "Operator was speaking or using a mobile phone instead of working.",

    OPERATOR_NOT_AVAILABLE:
        "Worker was not in the station and the station stood unmanned.",

    NON_PRODUCTIVE_TASK:
        "Operator wore PPE, cleaned the welding gun / torch, refilled or changed a "
        "consumable, or measured instead of building the part."

}


# ============================================================
# NVA CAUSES - THE PLANT'S NVA LIST
# ============================================================

IDLE_ABOVE_5_SEC = "Idle above 5 seconds"
SEARCHING_TOOLS = "Searching tools"
SEARCHING_MATERIALS = "Searching materials"
SPEAKING_REASON = "Speaking"
USING_MOBILE_PHONE = "Using mobile phone"
WAITING_FOR_TOOLS = "Waiting for tools"
WAITING_FOR_MATERIALS = "Waiting for materials"
WAITING_FOR_CRANE = "Waiting for crane"
TAKING_FIXTURE = "Taking fixture"
TAKING_TEMPLATE = "Taking template"
MOVING_FIXTURE = "Moving fixture"
MOVING_TEMPLATE = "Moving template"
REWORK_REASON = "Rework"
PPE_WEARING = "PPE wearing"
SEARCHING_DOCUMENTS = "Searching documents / drawing file"
WAITING_FOR_CO_WORKERS = "Waiting for co-workers"
WORKER_NOT_IN_STATION = "Worker not in station"
TORCH_CLEANING = "Welding gun / torch cleaning"
CONSUMABLE_CHANGE = (
    "Refill or change of consumables "
    "(coil refill, grinding wheel change, mirror replacement in shelling)"
)
MEASURING = "Measuring"


NVA_CAUSES = [
    IDLE_ABOVE_5_SEC,
    SEARCHING_TOOLS,
    SEARCHING_MATERIALS,
    SPEAKING_REASON,
    USING_MOBILE_PHONE,
    WAITING_FOR_TOOLS,
    WAITING_FOR_MATERIALS,
    WAITING_FOR_CRANE,
    TAKING_FIXTURE,
    TAKING_TEMPLATE,
    MOVING_FIXTURE,
    MOVING_TEMPLATE,
    REWORK_REASON,
    PPE_WEARING,
    SEARCHING_DOCUMENTS,
    WAITING_FOR_CO_WORKERS,
    WORKER_NOT_IN_STATION,
    TORCH_CLEANING,
    CONSUMABLE_CHANGE,
    MEASURING
]


# Each NVA cause rolls up into one of the eight conditions, so a
# reason supplied by the AI always lands in the right bucket.
REASON_TO_CATEGORY = {

    SEARCHING_TOOLS: SEARCHING_FOR_TOOLS,
    SEARCHING_MATERIALS: SEARCHING_FOR_TOOLS,
    SEARCHING_DOCUMENTS: SEARCHING_FOR_TOOLS,

    REWORK_REASON: REWORK,

    IDLE_ABOVE_5_SEC: IDLE_TIME,
    WAITING_FOR_TOOLS: IDLE_TIME,
    WAITING_FOR_MATERIALS: IDLE_TIME,
    WAITING_FOR_CRANE: IDLE_TIME,
    WAITING_FOR_CO_WORKERS: IDLE_TIME,

    TAKING_FIXTURE: EXCESS_MOVEMENT,
    TAKING_TEMPLATE: EXCESS_MOVEMENT,
    MOVING_FIXTURE: EXCESS_MOVEMENT,
    MOVING_TEMPLATE: EXCESS_MOVEMENT,

    SPEAKING_REASON: SPEAKING,
    USING_MOBILE_PHONE: SPEAKING,

    WORKER_NOT_IN_STATION: OPERATOR_NOT_AVAILABLE,

    PPE_WEARING: NON_PRODUCTIVE_TASK,
    TORCH_CLEANING: NON_PRODUCTIVE_TASK,
    CONSUMABLE_CHANGE: NON_PRODUCTIVE_TASK,
    MEASURING: NON_PRODUCTIVE_TASK

}


# The cause written into the report when a condition was detected
# from the video but the AI gave no usable reason of its own.
# Excess walking has no entry on the plant's NVA list, so it is
# reported under its own name.
CATEGORY_DEFAULT_REASON = {

    EXCESS_WALKING: "Excess walking",
    SEARCHING_FOR_TOOLS: SEARCHING_TOOLS,
    REWORK: REWORK_REASON,
    IDLE_TIME: IDLE_ABOVE_5_SEC,
    EXCESS_MOVEMENT: MOVING_FIXTURE,
    SPEAKING: SPEAKING_REASON,
    OPERATOR_NOT_AVAILABLE: WORKER_NOT_IN_STATION,
    NON_PRODUCTIVE_TASK: MEASURING

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
        "not at the workstation", "left the station", "no operator at",
        "not in station", "not in the station", "worker not in"
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

    # 6. Speaking / mobile phone
    (SPEAKING, [
        "talking", "talks", "speaking", "speaks", "conversation", "discussing",
        "discussion", "discusses", "chatting", "chat", "instructed", "instruction from",
        "asking", "asks a colleague", "phone", "mobile", "briefing", "explaining"
    ]),

    # 8. Non-productive task
    (NON_PRODUCTIVE_TASK, [
        "ppe", "wearing gloves", "wears gloves", "putting on gloves", "puts on gloves",
        "wearing helmet", "wears helmet", "welding helmet on", "safety goggles",
        "wearing the apron", "wearing apron", "torch cleaning", "cleaning the torch",
        "cleans the torch", "gun cleaning", "cleaning the welding gun",
        "cleans the welding gun", "nozzle cleaning", "cleaning the nozzle",
        "coil refill", "wire refill", "refilling", "refills", "changing the coil",
        "wire spool", "grinding wheel change", "changing the grinding wheel",
        "changes the grinding wheel", "wheel change", "replacing the mirror",
        "mirror replacement", "replaces the mirror", "consumable",
        "measuring", "measures", "measurement", "measuring tape", "tape measure",
        "vernier", "scale reading"
    ]),

    # 2. Searching for tools / materials / documents
    (SEARCHING_FOR_TOOLS, [
        "searching", "searches", "search", "looking for", "looks for", "hunting",
        "rummag", "find the tool", "finding the tool", "locate the tool",
        "tool not available", "tool missing", "checking the bin", "checks the bin",
        "opening bins", "scanning the bench", "pockets", "cannot find", "can not find"
    ]),

    # 5. Taking / moving fixtures and templates
    (EXCESS_MOVEMENT, [
        "taking fixture", "taking the fixture", "takes the fixture",
        "taking template", "taking the template", "takes the template",
        "picks up the fixture", "picking up the fixture",
        "picks up the template", "picking up the template",
        "moving fixture", "moving the fixture", "moves the fixture",
        "moving template", "moving the template", "moves the template",
        "carrying the fixture", "carries the fixture",
        "carrying the template", "carries the template",
        "over-reach", "overreach", "excess motion", "excessive motion",
        "unnecessary motion", "unnecessary movement", "excess movement",
        "excessive movement"
    ]),

    # 1. Excess walking
    (EXCESS_WALKING, [
        "walking", "walks", "walked", "steps across", "crosses the bay",
        "travels to", "goes to the rack", "goes to the bin", "trolley trip",
        "back and forth", "repeated trips", "fetch", "fetches"
    ]),

    # 4. Idle / waiting
    (IDLE_TIME, [
        "idle", "waiting", "waits", "stands by", "standing by", "stood by",
        "watching", "watches", "does nothing", "doing nothing", "pause", "delay",
        "holds up", "held up", "stalled"
    ])

]


# ============================================================
# KEYWORD -> NVA REASON
# ============================================================
#
# Picks the specific cause inside the detected condition.
# A reason is only used when it belongs to that condition,
# so the order here only matters within one condition.

KEYWORD_RULES = [

    # Operator not available
    ("not in station", WORKER_NOT_IN_STATION),
    ("not in the station", WORKER_NOT_IN_STATION),
    ("left the", WORKER_NOT_IN_STATION),
    ("absent", WORKER_NOT_IN_STATION),
    ("unmanned", WORKER_NOT_IN_STATION),

    # Rework
    ("rework", REWORK_REASON),

    # Speaking / mobile phone
    ("phone", USING_MOBILE_PHONE),
    ("mobile", USING_MOBILE_PHONE),
    ("talk", SPEAKING_REASON),
    ("speak", SPEAKING_REASON),
    ("discuss", SPEAKING_REASON),

    # Non-productive tasks
    ("ppe", PPE_WEARING),
    ("glove", PPE_WEARING),
    ("helmet", PPE_WEARING),
    ("goggle", PPE_WEARING),
    ("apron", PPE_WEARING),
    ("torch", TORCH_CLEANING),
    ("gun clean", TORCH_CLEANING),
    ("welding gun", TORCH_CLEANING),
    ("nozzle", TORCH_CLEANING),
    ("coil", CONSUMABLE_CHANGE),
    ("refill", CONSUMABLE_CHANGE),
    ("spool", CONSUMABLE_CHANGE),
    ("grinding wheel", CONSUMABLE_CHANGE),
    ("wheel change", CONSUMABLE_CHANGE),
    ("mirror", CONSUMABLE_CHANGE),
    ("consumable", CONSUMABLE_CHANGE),
    ("measur", MEASURING),
    ("vernier", MEASURING),
    ("tape", MEASURING),

    # Searching
    ("document", SEARCHING_DOCUMENTS),
    ("drawing", SEARCHING_DOCUMENTS),
    ("file", SEARCHING_DOCUMENTS),
    ("material", SEARCHING_MATERIALS),
    ("part", SEARCHING_MATERIALS),
    ("component", SEARCHING_MATERIALS),
    ("bolt", SEARCHING_MATERIALS),
    ("nut", SEARCHING_MATERIALS),
    ("tool", SEARCHING_TOOLS),
    ("spanner", SEARCHING_TOOLS),
    ("wrench", SEARCHING_TOOLS),

    # Fixtures and templates
    ("taking fixture", TAKING_FIXTURE),
    ("taking the fixture", TAKING_FIXTURE),
    ("takes the fixture", TAKING_FIXTURE),
    ("picks up the fixture", TAKING_FIXTURE),
    ("picking up the fixture", TAKING_FIXTURE),
    ("taking template", TAKING_TEMPLATE),
    ("taking the template", TAKING_TEMPLATE),
    ("takes the template", TAKING_TEMPLATE),
    ("picks up the template", TAKING_TEMPLATE),
    ("picking up the template", TAKING_TEMPLATE),
    ("template", MOVING_TEMPLATE),
    ("fixture", MOVING_FIXTURE),

    # Idle / waiting
    ("crane", WAITING_FOR_CRANE),
    ("hoist", WAITING_FOR_CRANE),
    ("co-worker", WAITING_FOR_CO_WORKERS),
    ("coworker", WAITING_FOR_CO_WORKERS),
    ("colleague", WAITING_FOR_CO_WORKERS),
    ("another operator", WAITING_FOR_CO_WORKERS),
    ("other operator", WAITING_FOR_CO_WORKERS),
    ("helper", WAITING_FOR_CO_WORKERS),
    ("waiting for tool", WAITING_FOR_TOOLS),
    ("waits for tool", WAITING_FOR_TOOLS),
    ("waiting for the tool", WAITING_FOR_TOOLS),
    ("waiting for material", WAITING_FOR_MATERIALS),
    ("waits for material", WAITING_FOR_MATERIALS),
    ("waiting for the material", WAITING_FOR_MATERIALS),
    ("waiting for part", WAITING_FOR_MATERIALS),
    ("waiting for the part", WAITING_FOR_MATERIALS),
    ("idle", IDLE_ABOVE_5_SEC)

]

# ============================================================
# NVA CATEGORY - THE EIGHT CONDITIONS
# ============================================================

def activity_text(activity):
    """
    What the AI observed in the video, lower-cased, so the eight
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
    Decide which of the eight NVA conditions an activity falls under.

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
    Non Value Added. Runs before the TOCT / NVA maths so the eight
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
    cause when one of the eight conditions actually flagged it.
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
