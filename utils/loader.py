import json
import pandas as pd
from pathlib import Path

from utils.export import to_operation_text, add_repeat_count


class TimeStudyLoader:

    def __init__(self, json_path):

        self.json_path = Path(json_path)

        self.data = None

        self.activities = pd.DataFrame()

        self.overall = {}

        self.operator_count = 5

        self.operator_summary = pd.DataFrame()

        self.nva_breakdown = {}

    # =====================================================
    # DEFAULT JSON
    # =====================================================

    def default_json(self):

        return {

            "video_summary": "No analysis available.",

            "management_summary": "Upload a manufacturing video to generate the report.",

            "video_file_name": "",

            "total_processes": 0,

            "activities": [],

            "operator_analysis": [],

            "overall_analysis": {

                "total_time_seconds": 0,

                "cycle_time_seconds": 0,

                "operator_working_time": 0,

                "walking_time": 0,

                "operator_waiting_time": 0,

                "rework_time": 0,

                "operator_idle_time": 0,

                "unaccounted_idle_time": 0,

                "inspection_time": 0,

                "estimated_value_added_time": 0,

                "estimated_non_value_added_time": 0

            },

            "lean_observations": [],

            "productivity_opportunities": []

        }

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        if not self.json_path.exists():

            self.data = self.default_json()

        elif self.json_path.stat().st_size == 0:

            self.data = self.default_json()

        else:

            with open(

                self.json_path,

                "r",

                encoding="utf-8"

            ) as f:

                self.data = json.load(f)

        # ---------------------------------------
        # Missing Keys
        # ---------------------------------------

        self.data.setdefault("video_summary", "")

        self.data.setdefault("management_summary", "")

        self.data.setdefault("video_file_name", "")

        self.data.setdefault("total_processes", 0)

        self.data.setdefault("activities", [])

        self.data.setdefault("operator_analysis", [])

        self.data.setdefault("lean_observations", [])

        self.data.setdefault("productivity_opportunities", [])

        self.data.setdefault(

            "overall_analysis",

            {}

        )

        # ---------------------------------------
        # Overall Defaults
        # ---------------------------------------

        overall = self.data["overall_analysis"]

        overall.setdefault("total_time_seconds", 0)

        overall.setdefault("cycle_time_seconds", 0)

        overall.setdefault("operator_working_time", 0)

        overall.setdefault("walking_time", 0)

        overall.setdefault("operator_waiting_time", 0)

        overall.setdefault("rework_time", 0)

        overall.setdefault("operator_idle_time", 0)

        overall.setdefault("unaccounted_idle_time", 0)

        overall.setdefault("inspection_time", 0)

        overall.setdefault("estimated_value_added_time", 0)

        overall.setdefault("estimated_non_value_added_time", 0)

        overall.setdefault("value_added_percent", 0)

        overall.setdefault("non_value_added_percent", 0)

        self.overall = overall

        # ---------------------------------------
        # NVA Breakdown - which activities are NVA
        # ---------------------------------------

        self.data.setdefault("nva_breakdown", {})

        breakdown = self.data["nva_breakdown"]

        breakdown.setdefault("by_category", [])

        breakdown.setdefault("activities", [])

        breakdown.setdefault("unrecorded_idle_seconds", 0)

        self.nva_breakdown = breakdown

        # ---------------------------------------
        # Activities
        # ---------------------------------------

        self.activities = pd.DataFrame(

            self.data["activities"]

        )

        required = [

            "process_no",

            "process_name",

            "process_operation",

            "process_description",

            "start_timestamp",

            "end_timestamp",

            "duration",

            "operator",

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

            "nva_reason",

            "walking_steps",

            "waste_type",

            "value_added"

        ]

        string_cols = {
            "process_description",
            "nva_category",
            "nva_reason",
            "waste_type",
            "value_added",
            "operator"
        }

        for col in required:

            if col not in self.activities.columns:

                self.activities[col] = "" if col in string_cols else 0

        # Older reports stored numbered SOP steps - show them operation-wise
        self.activities["process_description"] = (
            self.activities["process_description"].map(to_operation_text)
        )

        # ---------------------------------------
        # Operator Count (1 to 5)
        # ---------------------------------------

        raw_count = self.data.get("operator_count", 0) or 0

        if not raw_count:

            operators = set()

            for activity in self.data.get("activities", []):

                operator = str(
                    activity.get("operator", "") or ""
                ).strip()

                if operator:

                    operators.add(operator.lower())

            raw_count = max(len(operators), 1)

        self.operator_count = max(
            1,
            min(int(raw_count), 5)
        )

        # ---------------------------------------
        # Per Operator Summary
        # ---------------------------------------

        self.operator_summary = pd.DataFrame(

            self.data.get("operator_analysis", [])

        )

        return self.data

    # =====================================================
    # GETTERS
    # =====================================================

    def get_summary(self):

        return {

            "video_summary":

                self.data["video_summary"],

            "management_summary":

                self.data["management_summary"],

            "video_file_name":

                self.data.get("video_file_name", ""),

            "total_processes":

                self.data["total_processes"]

        }

    def get_overall(self):

        return self.overall

    def get_activity_dataframe(self):

        return self.activities

    def get_nva_breakdown(self):
        """
        The NVA rollup by condition plus the list of exactly which
        activities were charged as Non Value Added.
        """

        return self.nva_breakdown

    def get_nva_table(self):
        """
        The NVA activities with report-ready column names.
        """

        columns = [

            ("process_no", "Process No"),

            ("process_name", "Process Name"),

            ("repeat_count", "Repeat Count"),

            ("process_operation", "Operation"),

            ("start_timestamp", "Start Time"),

            ("end_timestamp", "End Time"),

            ("nva", "NVA (sec)"),

            ("nva_category", "NVA Condition"),

            ("nva_reason", "NVA Reason")

        ]

        rows = pd.DataFrame(
            add_repeat_count(self.nva_breakdown.get("activities", []))
        )

        if rows.empty:
            return pd.DataFrame(
                columns=[header for _, header in columns]
            )

        text_cols = {
            "process_name",
            "process_operation",
            "start_timestamp",
            "end_timestamp",
            "nva_category",
            "nva_reason"
        }

        for key, _ in columns:

            if key not in rows.columns:

                rows[key] = "" if key in text_cols else 0

        rows = rows[[key for key, _ in columns]]

        rows.columns = [header for _, header in columns]

        return rows

    def get_nva_category_table(self):
        """
        NVA time rolled up by each of the eight conditions.
        """

        columns = [

            ("nva_category", "NVA Condition"),

            ("definition", "What This Condition Means"),

            ("activities", "Activities"),

            ("nva_seconds", "NVA Time (sec)")

        ]

        rows = pd.DataFrame(
            self.nva_breakdown.get("by_category", [])
        )

        if rows.empty:
            return pd.DataFrame(
                columns=[header for _, header in columns]
            )

        for key, _ in columns:

            if key not in rows.columns:

                rows[key] = "" if key in {"nva_category", "definition"} else 0

        rows = rows[[key for key, _ in columns]]

        rows.columns = [header for _, header in columns]

        return rows

    def get_operator_count(self):

        return self.operator_count

    def get_operator_summary(self):
        """
        One row per operator observed in the video.
        Empty DataFrame when the study holds no operator breakdown.
        """

        return self.operator_summary

    def get_operator_table(self):
        """
        Operator summary with report-ready column names.
        """

        columns = [

            ("operator", "Operator"),

            ("processes", "Processes"),

            ("first_seen", "First Seen"),

            ("last_seen", "Last Seen"),

            ("study_window_seconds", "Cycle Window (sec)"),

            ("observed_time_seconds", "Observed Time (sec)"),

            ("working_time", "Working (sec)"),

            ("waiting_time", "Waiting (sec)"),

            ("walking_time", "Walking (sec)"),

            ("rework_time", "Required NVA (sec)"),

            ("idle_time", "Idle (sec)"),

            ("toct", "TOCT (sec)"),

            ("nva", "NVA (sec)"),

            ("utilisation_percent", "Utilisation %"),

            ("value_added_percent", "Value Added %")

        ]

        summary = self.operator_summary.copy()

        text_cols = {"operator", "first_seen", "last_seen"}

        for key, _ in columns:

            if key not in summary.columns:

                summary[key] = "" if key in text_cols else 0

        summary = summary[[key for key, _ in columns]]

        summary.columns = [header for _, header in columns]

        return summary

    def get_lean(self):

        return self.data["lean_observations"]

    def get_opportunities(self):

        return self.data["productivity_opportunities"]

    def get_json(self):

        return self.data