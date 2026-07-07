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

    # ---------------------------------------------
    # Save JSON
    # ---------------------------------------------
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    # ---------------------------------------------
    # Create DataFrame
    # ---------------------------------------------
    activities = pd.DataFrame(data["activities"])

    # ---------------------------------------------
    # Required Column Order
    # ---------------------------------------------
    required_columns = [
        "process_no",
        "process_name",
        "process_operation",
        "start_time",
        "end_time",
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

    # ---------------------------------------------
    # Add Missing Columns Automatically
    # ---------------------------------------------
    for col in required_columns:
        if col not in activities.columns:
            activities[col] = ""

    # ---------------------------------------------
    # Reorder Columns
    # ---------------------------------------------
    activities = activities[required_columns]

    # ---------------------------------------------
    # Rename Columns for Excel
    # ---------------------------------------------
    activities.columns = [
        "Process No",
        "Process Name",
        "Process Operation",
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
        "NVA (min)",
        "R-NVA (min)"
    ]

    # ---------------------------------------------
    # Save Excel
    # ---------------------------------------------
    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl"
    ) as writer:

        activities.to_excel(
            writer,
            sheet_name="Time Study",
            index=False
        )

        workbook = writer.book
        worksheet = writer.sheets["Time Study"]

        # Make header bold
        from openpyxl.styles import Font

        bold_font = Font(bold=True)

        for cell in worksheet[1]:
            cell.font = bold_font

        # Auto-fit columns
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 5

    # ---------------------------------------------
    # Save CSV
    # ---------------------------------------------
    activities.to_csv(
        CSV_FILE,
        index=False
    )

    print("✅ JSON Saved :", JSON_FILE)
    print("✅ Excel Saved:", EXCEL_FILE)
    print("✅ CSV Saved  :", CSV_FILE)

    return activities