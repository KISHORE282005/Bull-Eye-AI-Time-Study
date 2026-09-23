from google.genai import types  # Import types to configure the model
from .config import client, MODEL
from .prompts import TIME_STUDY_PROMPT
from .report import OUTPUT  # Project-root /output, not the current folder


def analyze_video(video, on_progress=None):
    # Reference the uploaded file by its URI instead of passing the object.
    video_part = types.Part.from_uri(
        file_uri=video.uri,
        mime_type=video.mime_type
    )

    response = client.models.generate_content_stream(
        model=MODEL,
        contents=[
            TIME_STUDY_PROMPT,
            video_part
        ],
        config=types.GenerateContentConfig(
            temperature=0.0,                         # 0.0 forces strict, factual outputs (no creativity/hallucinations)
            response_mime_type="application/json"    # Forces the API to ONLY return valid JSON
        )
    )

    # Accumulate the streamed chunks into one JSON string.
    parts = []
    for chunk in response:
        if chunk.text:
            parts.append(chunk.text)
            if on_progress is not None:
                on_progress(len("".join(parts)))

    text = "".join(parts)

    if not text:
        raise RuntimeError("Gemini returned an empty response.")

    # Save raw Gemini response
    response_file = OUTPUT / "gemini_response.txt"

    with open(response_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Gemini response saved to {response_file}")

    return text
