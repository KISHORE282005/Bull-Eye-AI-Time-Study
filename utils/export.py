import json
import re
import pandas as pd
from pathlib import Path
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.utils import get_column_letter

from utils.nva_reasons import NVA_CATEGORIES


# ==========================================================
# REPORT FORMATTING HELPERS
# ==========================================================

_STEP_NUMBER = re.compile(r"(?:^|(?<=\s))(?:step\s*)?\d+\s*[.)]\s+", re.IGNORECASE)


def to_operation_text(text):
    """
    Return the process description in operation-wise format: one
    running paragraph that names the operation, e.g.

        Torque fastening operation - tightening the chassis side
        bracket bolts with a pneumatic impact wrench ...

    Older reports stored numbered SOP steps ("1. ...\\n2. ..."); the
    step numbers and line breaks are removed so they read the same way.
    Running it twice gives the same result.
    """

    text = str(text or "").strip()

    if not text:
        return ""

    text = _STEP_NUMBER.sub("", text)

    return " ".join(text.split())


def format_sec_min(seconds):
    """125.4 -> '125.40 sec (2.09 min)'"""

    seconds = float(seconds or 0)

    return f"{seconds:.2f} sec ({seconds / 60:.2f} min)"


def _activity_key(name):
    return " ".join(str(name or "").lower().split())


def add_repeat_count(activities):
    """
    Give every NVA activity a `repeat_count`: how many NVA activities
    in the list carry the same process name (case and spacing ignored).
    """

    activities = [dict(activity) for activity in (activities or [])]

    counts = {}

    for activity in activities:
        key = _activity_key(activity.get("process_name", ""))
        counts[key] = counts.get(key, 0) + 1

    for activity in activities:
        activity["repeat_count"] = counts[
            _activity_key(activity.get("process_name", ""))
        ]

    return activities


# ==========================================================
# REQUIRED COLUMN ORDER
# ==========================================================

REPORT_COLUMNS = [
    "process_no",
    "process_name",
    "process_operation",

    # The description explains what the person is doing and which
    # industrial process it belongs to - the heart of the study
    "process_description",

    "start_timestamp",
    "end_timestamp",
    "duration",

    "op1",
    "op2",
    "op3",
    "op4",
    "op5",

    "op_wt1",
    "op_wt2",
    "op_wt3",
    "op_wt4",
    "op_wt5",

    "toct",
    "va",
    "nva",
    "r_nva",
    "nva_category",
    "nva_reason"
]

REPORT_HEADERS = [
    "Process No",
    "Process Name",
    "Process Operation",
    "Process Description",
    "Start Time",
    "End Time",
    "Duration",

    "Op1 (min)",
    "Op2 (min)",
    "Op3 (min)",
    "Op4 (min)",
    "Op5 (min)",

    "Op WT1 (min)",
    "Op WT2 (min)",
    "Op WT3 (min)",
    "Op WT4 (min)",
    "Op WT5 (min)",

    "TOCT (min)",
    "VA (min)",
    "NVA (min)",
    "Required NVA (min)",
    "NVA Category",
    "NVA Reason"
]


# ==========================================================
# OVERALL ANALYSIS SHEET
# ==========================================================
#
# One sheet that answers three questions:
#
#   1. How long did the job take, and how much of it was
#      Value Added versus Non Value Added?
#   2. Which of the seven NVA conditions cost the most time?
#   3. WHICH ACTIVITIES are the NVA - the seven conditions with
#      a count of processes in each. Click a count to jump to
#      the NVA Details sheet, which lists those processes.
#
# The NVA figure at the top is a link. Click it and Excel
# jumps straight to the NVA list. Each process on the NVA
# Details sheet links back to its row on the Time Study sheet.
# ==========================================================

SECTION_FILL = PatternFill(fill_type="solid", fgColor="C00000")
SECTION_FONT = Font(bold=True, color="FFFFFF", size=12)

HEAD_FILL = PatternFill(fill_type="solid", fgColor="404040")
HEAD_FONT = Font(bold=True, color="FFFFFF")

TOTAL_FILL = PatternFill(fill_type="solid", fgColor="F2F2F2")
TOTAL_FONT = Font(bold=True)

VA_FONT = Font(bold=True, color="006100")
NVA_FONT = Font(bold=True, color="9C0006")
LINK_FONT = Font(bold=True, color="0563C1", underline="single")

LEFT = Alignment(horizontal="left", vertical="top", wrap_text=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


# Pretty names for the raw overall_analysis keys
OVERALL_LABELS = {
    "total_time_seconds": "Total Time (sec)",
    "cycle_time_seconds": "Cycle Time (sec)",
    "operator_count": "Operators",
    "operator_working_time": "Operator Working Time (sec)",
    "walking_time": "Walking Time (sec)",
    "operator_waiting_time": "Operator Waiting Time (sec)",
    "rework_time": "Required NVA Time (sec)",
    "operator_idle_time": "Operator Idle Time (sec)",
    "unaccounted_idle_time": "Unrecorded Idle Time (sec)",
    "inspection_time": "Inspection Time (sec)",
    "estimated_value_added_time": "Value Added (VA) Time (sec)",
    "estimated_non_value_added_time": "Non Value Added (NVA) Time (sec)",
    "value_added_percent": "Value Added (VA) %",
    "non_value_added_percent": "Non Value Added (NVA) %",
    "average_operator_utilisation_percent": "Average Operator Utilisation %"
}


def _percent(part, whole):
    """part as a percentage of whole, safe when whole is zero."""

    if not whole:
        return 0.0

    return round((part / whole) * 100, 1)


def _section(worksheet, row, title, width):
    """Write a full-width red section banner and return the next row."""

    worksheet.cell(row=row, column=1, value=title)

    worksheet.merge_cells(
        start_row=row,
        start_column=1,
        end_row=row,
        end_column=width
    )

    for column in range(1, width + 1):

        cell = worksheet.cell(row=row, column=column)

        cell.fill = SECTION_FILL
        cell.font = SECTION_FONT
        cell.alignment = Alignment(horizontal="left", vertical="center")

    worksheet.row_dimensions[row].height = 22

    return row + 1


def _head(worksheet, row, headers):
    """Write a dark column-header strip and return the next row."""

    for column, title in enumerate(headers, start=1):

        cell = worksheet.cell(row=row, column=column, value=title)

        cell.fill = HEAD_FILL
        cell.font = HEAD_FONT
        cell.alignment = CENTER

    return row + 1


def _link(cell, location, text=None):
    """Turn a cell into a clickable jump to another place in the book."""

    if text is not None:
        cell.value = text

    cell.hyperlink = Hyperlink(
        ref=cell.coordinate,
        location=location
    )

    cell.font = LINK_FONT


NVA_DETAILS_SHEET = "NVA Details"


def _write_nva_details_sheet(
    overall_sheet,
    members_by_condition,
    list_row,
    time_study_sheet,
    time_study_rows
):
    """
    Build the NVA Details sheet next to the Overall Analysis sheet:
    one block per NVA condition that has processes, listing Process
    No, Process Name, Start / End Time and NVA sec.

    Returns {condition: first row of its block}, so the counts on
    the Overall Analysis sheet can link straight to it.
    """

    workbook = overall_sheet.parent

    if NVA_DETAILS_SHEET in workbook.sheetnames:
        del workbook[NVA_DETAILS_SHEET]

    sheet = workbook.create_sheet(
        NVA_DETAILS_SHEET,
        workbook.index(overall_sheet) + 1
    )

    back = f"'{overall_sheet.title}'!A{list_row}"

    width = 5

    row = 1

    targets = {}

    for condition, members in members_by_condition.items():

        if not members:
            continue

        targets[condition] = row

        row = _section(
            sheet,
            row,
            f"{condition.upper()} - {len(members)} "
            f"{'PROCESS' if len(members) == 1 else 'PROCESSES'}",
            width
        )

        row = _head(
            sheet,
            row,
            ["Process No", "Process Name", "Start Time", "End Time", "NVA Time (sec)"]
        )

        for entry in members:

            process_no = entry.get("process_no", "")

            number_cell = sheet.cell(row=row, column=1, value=process_no)

            # Link the process number back to its row on the Time
            # Study sheet, so the reader can see it in context.

            target = time_study_rows.get(process_no)

            if target:

                _link(
                    number_cell,
                    f"'{time_study_sheet}'!A{target}"
                )

            sheet.cell(row=row, column=2, value=entry.get("process_name", ""))
            sheet.cell(row=row, column=3, value=entry.get("start_timestamp", ""))
            sheet.cell(row=row, column=4, value=entry.get("end_timestamp", ""))
            sheet.cell(row=row, column=5, value=entry.get("nva", 0)).font = NVA_FONT

            row += 1

        _link(
            sheet.cell(row=row, column=1),
            back,
            "<< Back to NVA activities"
        )

        row += 2

    if not targets:

        sheet.cell(
            row=1,
            column=1,
            value="No activity matched any of the seven NVA conditions."
        )

    for index, size in enumerate([16, 46, 16, 16, 16], start=1):

        sheet.column_dimensions[get_column_letter(index)].width = size

    return targets


def write_overall_analysis_sheet(
    worksheet,
    overall,
    nva_breakdown,
    total_processes=0,
    time_study_sheet="Time Study",
    time_study_rows=None
):
    """
    Build the Overall Analysis sheet.

    time_study_rows maps a process number to its row on the Time Study
    sheet, so every NVA activity can link back to where it came from.
    """

    overall = overall or {}

    nva_breakdown = nva_breakdown or {}

    time_study_rows = time_study_rows or {}

    sheet_name = worksheet.title

    categories = nva_breakdown.get("by_category", []) or []

    nva_activities = add_repeat_count(
        nva_breakdown.get("activities", []) or []
    )

    unrecorded_idle = round(
        nva_breakdown.get("unrecorded_idle_seconds", 0) or 0,
        3
    )

    total_time = round(overall.get("total_time_seconds", 0) or 0, 3)

    va_time = round(overall.get("estimated_value_added_time", 0) or 0, 3)

    nva_time = round(overall.get("estimated_non_value_added_time", 0) or 0, 3)

    rework_time = round(overall.get("rework_time", 0) or 0, 3)

    accounted = round(va_time + nva_time, 3)

    width = 10

    row = 1

    # ------------------------------------------------------
    # 1. HEADLINE - TOTAL TIME / VA / NVA
    # ------------------------------------------------------

    row = _section(worksheet, row, "TIME STUDY SUMMARY", width)

    row = _head(
        worksheet,
        row,
        ["Metric", "Time (sec)", "Time (min)", "% of Work Content"]
    )

    headline = [
        ("Total Time", total_time, 100.0, None),
        ("Value Added (VA) Time", va_time, _percent(va_time, accounted), VA_FONT),
        ("Non Value Added (NVA) Time", nva_time, _percent(nva_time, accounted), NVA_FONT),
        ("Required NVA (R-NVA) Time", rework_time, _percent(rework_time, accounted), None)
    ]

    nva_row = None

    for label, seconds, percent, font in headline:

        worksheet.cell(row=row, column=1, value=label)
        worksheet.cell(row=row, column=2, value=seconds)
        worksheet.cell(row=row, column=3, value=round(seconds / 60, 3))
        worksheet.cell(row=row, column=4, value=f"{percent}%")

        if font is not None:

            for column in range(1, 5):
                worksheet.cell(row=row, column=column).font = font

        if label.startswith("Non Value Added"):
            nva_row = row

        row += 1

    worksheet.cell(row=row, column=1, value="Operators")
    worksheet.cell(row=row, column=2, value=overall.get("operator_count", 1))
    row += 1

    row += 1

    # ------------------------------------------------------
    # 2. NVA BY CONDITION
    # ------------------------------------------------------

    category_row = row

    row = _section(
        worksheet,
        row,
        "NVA BREAKDOWN - WHICH CONDITION COST THE TIME",
        width
    )

    row = _head(
        worksheet,
        row,
        [
            "NVA Condition",
            "What This Condition Means",
            "Activities",
            "NVA Time (sec)",
            "% of NVA",
            "% of Total Time"
        ]
    )

    # Condition -> its "Activities" cell here, linked to the NVA list below
    category_count_cells = {}

    if categories:

        for entry in categories:

            seconds = round(entry.get("nva_seconds", 0) or 0, 3)

            category_count_cells[entry.get("nva_category", "")] = (
                worksheet.cell(row=row, column=3)
            )

            worksheet.cell(row=row, column=1, value=entry.get("nva_category", ""))
            worksheet.cell(row=row, column=2, value=entry.get("definition", ""))
            worksheet.cell(row=row, column=3, value=entry.get("activities", 0))
            worksheet.cell(row=row, column=4, value=seconds)
            worksheet.cell(row=row, column=5, value=f"{_percent(seconds, nva_time)}%")
            worksheet.cell(row=row, column=6, value=f"{_percent(seconds, total_time)}%")

            worksheet.cell(row=row, column=2).alignment = LEFT

            row += 1

        if unrecorded_idle > 0:

            worksheet.cell(
                row=row,
                column=2,
                value=(
                    f"Of the idle time above, {unrecorded_idle} sec is time inside the "
                    "study window that no activity was recorded for at all."
                )
            ).alignment = LEFT

            row += 1

        for column in range(1, 7):

            cell = worksheet.cell(row=row, column=column)

            cell.fill = TOTAL_FILL
            cell.font = TOTAL_FONT

        worksheet.cell(row=row, column=1, value="TOTAL NVA")
        worksheet.cell(row=row, column=3, value=len(nva_activities))
        worksheet.cell(row=row, column=4, value=nva_time)
        worksheet.cell(row=row, column=5, value="100.0%")
        worksheet.cell(row=row, column=6, value=f"{_percent(nva_time, total_time)}%")

        row += 1

    else:

        worksheet.cell(
            row=row,
            column=1,
            value="No non-value-added activity was detected in this video."
        )

        row += 1

    row += 1

    # ------------------------------------------------------
    # 3. NVA ACTIVITIES - ONE ROW PER NVA CONDITION
    #
    # Each of the seven NVA conditions gets a row with the count
    # of processes that fell into it (a repeated activity counts
    # every time it happens). Click the count to jump to the
    # "NVA Details" sheet, which lists those processes: Process
    # No, Process Name, timestamps and NVA sec.
    # ------------------------------------------------------

    detail_row = row

    row = _section(
        worksheet,
        row,
        "NVA ACTIVITIES - CLICK THE COUNT TO SEE THE PROCESSES",
        width
    )

    row = _head(
        worksheet,
        row,
        ["NVA Condition", "Count", "NVA Time (sec)"]
    )

    seconds_by_category = {
        entry.get("nva_category", ""): round(entry.get("nva_seconds", 0) or 0, 3)
        for entry in categories
    }

    members_by_condition = {
        condition: sorted(
            (
                entry for entry in nva_activities
                if entry.get("nva_category", "") == condition
            ),
            key=lambda entry: entry.get("process_no", 0) or 0
        )
        for condition in NVA_CATEGORIES
    }

    count_cells = {}

    for condition in NVA_CATEGORIES:

        members = members_by_condition[condition]

        seconds = seconds_by_category.get(
            condition,
            round(sum(entry.get("nva", 0) or 0 for entry in members), 3)
        )

        worksheet.cell(row=row, column=1, value=condition)
        worksheet.cell(row=row, column=3, value=seconds)

        count_cells[condition] = worksheet.cell(
            row=row,
            column=2,
            value=len(members)
        )

        if members:

            worksheet.cell(row=row, column=1).font = NVA_FONT
            worksheet.cell(row=row, column=3).font = NVA_FONT

        row += 1

    for column in range(1, 4):

        cell = worksheet.cell(row=row, column=column)

        cell.fill = TOTAL_FILL
        cell.font = TOTAL_FONT

    worksheet.cell(row=row, column=1, value="TOTAL NVA")
    worksheet.cell(row=row, column=2, value=len(nva_activities))
    worksheet.cell(row=row, column=3, value=nva_time)

    row += 2

    # ------------------------------------------------------
    # NVA Details sheet - the processes behind each count
    # ------------------------------------------------------

    details = _write_nva_details_sheet(
        worksheet,
        members_by_condition,
        list_row=detail_row,
        time_study_sheet=time_study_sheet,
        time_study_rows=time_study_rows
    )

    for condition, target in details.items():

        location = f"'{NVA_DETAILS_SHEET}'!A{target}"

        _link(count_cells[condition], location)

        # The "Activities" count in the breakdown above jumps
        # to the same place

        if condition in category_count_cells:
            _link(category_count_cells[condition], location)

    # ------------------------------------------------------
    # 4. EVERY METRIC
    # ------------------------------------------------------

    row = _section(worksheet, row, "OVERALL ANALYSIS - ALL METRICS", width)

    row = _head(worksheet, row, ["Metric", "Value"])

    for key, value in overall.items():

        worksheet.cell(row=row, column=1, value=OVERALL_LABELS.get(key, key))
        worksheet.cell(row=row, column=2, value=value)

        row += 1

        if key == "total_time_seconds":

            worksheet.cell(row=row, column=1, value="Total Time (min)")
            worksheet.cell(row=row, column=2, value=round((value or 0) / 60, 3))

            row += 1

    # ------------------------------------------------------
    # Make the NVA headline clickable
    # ------------------------------------------------------

    if nva_row is not None and nva_activities:

        _link(
            worksheet.cell(row=nva_row, column=1),
            f"'{sheet_name}'!A{detail_row}",
            "Non Value Added (NVA) Time  >>  click to see the activities"
        )

        _link(
            worksheet.cell(row=nva_row, column=2),
            f"'{sheet_name}'!A{category_row}",
            nva_time
        )

    # ------------------------------------------------------
    # Column widths
    # ------------------------------------------------------

    widths = [34, 46, 14, 16, 16, 16, 16, 24, 32]

    # Row 1 is a merged banner, so the letter comes from the index
    # rather than from the cell.

    for index, size in enumerate(widths, start=1):

        worksheet.column_dimensions[
            get_column_letter(index)
        ].width = size

    return worksheet


# ==========================================================
# JSON
# ==========================================================

def export_json(data):

    return json.dumps(
        data,
        indent=4,
        ensure_ascii=False
    )


# ==========================================================
# CSV
# ==========================================================

def export_csv(df):

    df = prepare_dataframe(df)

    return df.to_csv(
        index=False
    ).encode("utf-8")


# ==========================================================
# PREPARE DATAFRAME
# ==========================================================

def prepare_dataframe(df):

    df = df.copy()

    for col in REPORT_COLUMNS:

        if col not in df.columns:

            df[col] = ""

    df["process_description"] = df["process_description"].map(to_operation_text)

    df = df[REPORT_COLUMNS]

    df.columns = REPORT_HEADERS

    return df


# ==========================================================
# EXCEL
# ==========================================================

def export_excel(

    activities_df,

    overall,

    lean,

    opportunities,

    summary,

    nva_breakdown=None,

    total_processes=0

):

    output = BytesIO()

    raw_activities = activities_df

    activities_df = prepare_dataframe(activities_df)

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        ##################################################
        # Activities
        ##################################################

        activities_df.to_excel(
            writer,
            sheet_name="Time Study",
            index=False
        )

        ##################################################
        # Lean
        ##################################################

        pd.DataFrame({

            "Lean Observation":lean

        }).to_excel(

            writer,

            sheet_name="Lean Analysis",

            index=False

        )

        ##################################################
        # Opportunities
        ##################################################

        pd.DataFrame({

            "Improvement Opportunity":opportunities

        }).to_excel(

            writer,

            sheet_name="Improvement",

            index=False

        )

        ##################################################
        # Summary
        ##################################################

        pd.DataFrame(

            [summary]

        ).to_excel(

            writer,

            sheet_name="Summary",

            index=False

        )

        ##################################################
        # Formatting
        ##################################################

        workbook = writer.book

        header_fill = PatternFill(

            fill_type="solid",

            fgColor="1F4E78"

        )

        header_font = Font(

            color="FFFFFF",

            bold=True

        )

        for sheet in workbook.worksheets:

            for cell in sheet[1]:

                cell.fill = header_fill

                cell.font = header_font

                cell.alignment = Alignment(

                    horizontal="center",

                    vertical="center"

                )

            for column_cells in sheet.columns:

                length = max(

                    len(str(cell.value))

                    if cell.value else 0

                    for cell in column_cells

                )

                sheet.column_dimensions[

                    column_cells[0].column_letter

                ].width = min(length + 4, 60)

        ##################################################
        # Overall Analysis
        #
        # Built last, and deliberately AFTER the loop
        # above, so its banners and column widths are
        # not overwritten by the generic formatting.
        ##################################################

        overall_sheet = workbook.create_sheet(
            "Overall Analysis",
            1
        )

        time_study_rows = {
            process_no: index + 2
            for index, process_no in enumerate(
                activities_df["Process No"].tolist()
            )
        }

        if nva_breakdown is None:

            nva_breakdown = build_nva_breakdown(
                raw_activities,
                overall
            )

        write_overall_analysis_sheet(

            overall_sheet,

            overall,

            nva_breakdown,

            total_processes=total_processes or len(activities_df),

            time_study_sheet="Time Study",

            time_study_rows=time_study_rows

        )

    output.seek(0)

    return output


# ==========================================================
# NVA BREAKDOWN FROM A DATAFRAME
# ==========================================================

def build_nva_breakdown(activities_df, overall=None):
    """
    Rebuild the NVA breakdown from an activities DataFrame.

    The saved JSON already carries `nva_breakdown`; this is the
    fallback for an older report that does not.
    """

    from utils.calculations import calculate_nva_breakdown

    if activities_df is None or len(activities_df) == 0:
        return {}

    overall = overall or {}

    return calculate_nva_breakdown(

        activities_df.to_dict("records"),

        (overall or {}).get("unaccounted_idle_time", 0)

    )


# ==========================================================
# KPI
# ==========================================================

def kpi_dataframe(overall):

    return pd.DataFrame({

        "Metric":[

            "Cycle Time",

            "Working Time",

            "Walking Time",

            "Idle Time",

            "Value Added Time",

            "Non Value Added Time"

        ],

        "Value":[

            overall.get("cycle_time_seconds",0),

            overall.get("operator_working_time",0),

            overall.get("walking_time",0),

            overall.get("operator_idle_time",0),

            overall.get("estimated_value_added_time",0),

            overall.get("estimated_non_value_added_time",0)

        ]

    })


# ==========================================================
# SAVE JSON
# ==========================================================

def save_json(

    data,

    file_path

):

    file_path = Path(file_path)

    with open(

        file_path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            data,

            f,

            indent=4,

            ensure_ascii=False

        )


# ==========================================================
# SAVE CSV
# ==========================================================

def save_csv(

    df,

    file_path

):

    df = prepare_dataframe(df)

    df.to_csv(

        file_path,

        index=False

    )


# ==========================================================
# SAVE EXCEL
# ==========================================================

def save_excel(

    excel_bytes,

    file_path

):

    with open(

        file_path,

        "wb"

    ) as f:

        f.write(

            excel_bytes.getbuffer()

        )