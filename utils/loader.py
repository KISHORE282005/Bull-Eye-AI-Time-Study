import json
import pandas as pd
from pathlib import Path


class TimeStudyLoader:

    def __init__(self, json_path):

        self.json_path = Path(json_path)

        self.data = None

        self.activities = pd.DataFrame()

        self.overall = {}

        self.operator_count = 5

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

        self.overall = overall

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

            "nva",

            "r_nva",

            "nva_reason",

            "waste_type",

            "value_added"

        ]

        string_cols = {"nva_reason", "waste_type", "value_added", "operator"}

        for col in required:

            if col not in self.activities.columns:

                self.activities[col] = "" if col in string_cols else 0

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

    def get_lean(self):

        return self.data["lean_observations"]

    def get_opportunities(self):

        return self.data["productivity_opportunities"]

    def get_json(self):

        return self.data