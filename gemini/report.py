import json
import pandas as pd
from pathlib import Path

# =========================================================
# OUTPUT FOLDER
# =========================================================

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

JSON_FILE = OUTPUT / "time_study.json"
EXCEL_FILE = OUTPUT / "Industrial_Time_Study_Report.xlsx"
CSV_FILE = OUTPUT / "activities.csv"

# =========================================================
# SAVE REPORT
# =========================================================

def save_report(data):

    # -------------------------------------------------
    # Save JSON
    # -------------------------------------------------

    with open(JSON_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    # -------------------------------------------------
    # Activities DataFrame
    # -------------------------------------------------

    activities = pd.DataFrame(
        data.get("activities", [])
    )

    # -------------------------------------------------
    # Required Columns
    # -------------------------------------------------

    required_columns = [

        "process_no",

        "process_name",

        "process_operation",

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

        "nva",

        "r_nva"

    ]

    # -------------------------------------------------
    # Add Missing Columns
    # -------------------------------------------------

    for column in required_columns:

        if column not in activities.columns:

            if column in [

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
                "nva",
                "r_nva"

            ]:

                activities[column] = 0.0

            else:

                activities[column] = ""

    # -------------------------------------------------
    # Arrange Columns
    # -------------------------------------------------

    activities = activities[
        required_columns
    ]

    # -------------------------------------------------
    # Rename Excel Columns
    # -------------------------------------------------

    activities.columns = [

        "Process No",

        "Process Name",

        "Process Operation",

        "Process Description",

        "Start Timestamp",

        "End Timestamp",

        "Duration (sec)",

        "Op1 (sec)",
        "Op2 (sec)",
        "Op3 (sec)",
        "Op4 (sec)",
        "Op5 (sec)",

        "WT1 (sec)",
        "WT2 (sec)",
        "WT3 (sec)",
        "WT4 (sec)",
        "WT5 (sec)",

        "TOCT (sec)",

        "NVA (sec)",

        "R-NVA (sec)"

    ]
    # -------------------------------------------------
    # Save Excel
    # -------------------------------------------------

    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl"
    ) as writer:

        # ---------------------------------------------
        # Time Study Sheet
        # ---------------------------------------------

        activities.to_excel(
            writer,
            sheet_name="Time Study",
            index=False
        )

        workbook = writer.book
        worksheet = writer.sheets["Time Study"]

        from openpyxl.styles import Font, PatternFill, Alignment

        # ---------------------------------------------
        # Header Style
        # ---------------------------------------------

        header_font = Font(
            bold=True,
            color="FFFFFF"
        )

        header_fill = PatternFill(
            fill_type="solid",
            fgColor="C00000"
        )

        center = Alignment(
            horizontal="center",
            vertical="center"
        )

        for cell in worksheet[1]:

            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center

        # ---------------------------------------------
        # Auto Fit Columns
        # ---------------------------------------------

        for column_cells in worksheet.columns:

            length = max(
                len(str(cell.value))
                if cell.value else 0
                for cell in column_cells
            )

            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = length + 5

        # ---------------------------------------------
        # Freeze Header
        # ---------------------------------------------

        worksheet.freeze_panes = "A2"

        # ---------------------------------------------
        # Overall Analysis Sheet
        # ---------------------------------------------

        overall = pd.DataFrame(

            list(
                data.get(
                    "overall_analysis",
                    {}
                ).items()
            ),

            columns=[
                "Metric",
                "Value"
            ]

        )

        overall.to_excel(

            writer,

            sheet_name="Overall Analysis",

            index=False

        )

        overall_sheet = writer.sheets[
            "Overall Analysis"
        ]

        for cell in overall_sheet[1]:

            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center

        for column_cells in overall_sheet.columns:

            length = max(

                len(str(cell.value))
                if cell.value else 0

                for cell in column_cells

            )

            overall_sheet.column_dimensions[
                column_cells[0].column_letter
            ].width = length + 5

    # -------------------------------------------------
    # Save CSV
    # -------------------------------------------------

    activities.to_csv(

        CSV_FILE,

        index=False

    )

    # -------------------------------------------------
    # Console Messages
    # -------------------------------------------------

    print("=" * 60)

    print("Industrial AI Time Study Report Generated")

    print("=" * 60)

    print(f"JSON  : {JSON_FILE}")

    print(f"Excel : {EXCEL_FILE}")

    print(f"CSV   : {CSV_FILE}")

    print("=" * 60)

    return activities
