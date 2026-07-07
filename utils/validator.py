# ==========================================
# VALIDATION FUNCTIONS
# ==========================================

def validate_duration(duration):
    """
    Duration should not be negative.
    """

    return duration >= 0


def validate_toct(duration, toct):
    """
    TOCT should equal Duration.
    """

    return abs(duration - toct) <= 0.01


def validate_nva(toct, nva):
    """
    NVA cannot exceed TOCT.
    """

    return nva <= toct


def validate_rnva(nva, rnva):
    """
    R-NVA cannot exceed NVA.
    """

    return rnva <= nva


def validate_process(row):
    """
    Validate one process row.
    """

    errors = []

    if not validate_duration(row["duration"]):
        errors.append("Negative Duration")

    if not validate_toct(row["duration"], row["toct"]):
        errors.append("TOCT Mismatch")

    if not validate_nva(row["toct"], row["nva"]):
        errors.append("NVA > TOCT")

    if not validate_rnva(row["nva"], row["r_nva"]):
        errors.append("R-NVA > NVA")

    return errors