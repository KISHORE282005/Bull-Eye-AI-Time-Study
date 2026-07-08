import json


REQUIRED_FIELDS = [
    "process_no",
    "process_name",
    "process_operation",
    "process_description",
    "start_timestamp",
    "end_timestamp"
]


def parse_json(text):
    """
    Parse Gemini JSON response and validate the structure.
    """

    text = text.strip()

    # Remove markdown if Gemini returns it
    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.endswith("```"):
        text = text.replace("```", "")

    # Convert JSON string to Python dictionary
    data = json.loads(text)

    # Validate root keys
    if "activities" not in data:
        raise ValueError("Missing 'activities' in Gemini response.")

    # Validate each activity
    for index, activity in enumerate(data["activities"], start=1):

        for field in REQUIRED_FIELDS:

            if field not in activity:
                raise ValueError(
                    f"Activity {index} is missing '{field}'."
                )

    return data