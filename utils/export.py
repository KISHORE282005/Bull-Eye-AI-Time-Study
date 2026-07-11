import json
import pandas as pd
from pathlib import Path
from io import BytesIO
from openpyxl.styles import Font, PatternFill, Alignment


# ==========================================================
# REQUIRED COLUMN ORDER
# ==========================================================

REPORT_COLUMNS = [
    "process_no",
    "process_name",
    "process_operation",
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

REPORT_HEADERS = [
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

    summary

):

    output = BytesIO()

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
        # Overall
        ##################################################

        pd.DataFrame(
            [overall]
        ).to_excel(
            writer,
            sheet_name="Overall Analysis",
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

                ].width = length + 4

    output.seek(0)

    return output


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