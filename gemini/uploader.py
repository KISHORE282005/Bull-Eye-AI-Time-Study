import time

from google.genai import types

from .config import client


def upload_video(video_path):

    file = client.files.upload(
        file=video_path
    )

    # Wait until Gemini finishes processing the video on their servers.
    while file.state in (
        types.FileState.STATE_UNSPECIFIED,
        types.FileState.PROCESSING,
    ):

        time.sleep(5)

        file = client.files.get(
            name=file.name
        )

    if file.state != types.FileState.ACTIVE:

        raise RuntimeError(
            f"Video upload failed (state={file.state.name}). "
            "Try a smaller or shorter video."
        )

    return file


def delete_gemini_file(file_name):
    """Delete uploaded video from Gemini cloud storage."""
    try:
        client.files.delete(name=file_name)
    except Exception:
        pass
