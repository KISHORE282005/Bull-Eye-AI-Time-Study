from .config import client, MODEL
from .prompts import TIME_STUDY_PROMPT


def analyze_video(video):

    response = client.models.generate_content(

        model=MODEL,

        contents=[
            TIME_STUDY_PROMPT,
            video
        ]

    )

    # Save raw Gemini response
    with open("output/gemini_response.txt", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("✅ Gemini response saved to output/gemini_response.txt")

    return response.text