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
    "Communication delay"
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
# ASSIGN NVA REASON
# ============================================================

def assign_nva_reason(activity):
    """
    Pick the most specific NVA cause for a non-value-added activity
    using keyword matching over process_name / process_operation /
    process_description. Returns '' for value-added (Working) activities.
    """

    from utils.calculations import classify_activity

    activity_type = activity.get(
        "activity_type",
        classify_activity(
            activity.get("process_operation", "")
        )
    )

    if activity_type != "Working" and activity.get("nva", 0) > 0:

        existing = str(
            activity.get("nva_reason", "")
        ).strip()

        if existing and existing in NVA_CAUSES:
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

        if not text:
            if activity_type == "Rework":
                return "Rework"
            if activity_type == "Walking":
                return "Excessive walking"
            return "Waiting for material availability"

        for keyword, reason in KEYWORD_RULES:

            if keyword in text:
                return reason

        # Fallback by activity type
        if activity_type == "Rework":
            return "Rework"

        if activity_type == "Walking":
            return "Excessive walking"

        if activity_type == "Waiting":
            return "Waiting for material availability"

    return ""


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
