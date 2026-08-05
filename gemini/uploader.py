import os
import subprocess
import tempfile
import time
from pathlib import Path

from google.genai import types

from .config import client


# =========================================================
# EXTENSIONS THAT GEMINI DOES NOT ACCEPT -> MUST CONVERT
# =========================================================

CONVERT_EXTENSIONS = {
    ".mts",
    ".m2ts",
    ".m2t",
    ".ts",
    ".mt2s",
    ".m2p",
    ".tod",
    ".mod",
}


def convert_to_mp4(video_path):
    """
    Convert an unsupported video (e.g. .MTS / AVCHD) to .mp4
    using the ffmpeg binary bundled with imageio-ffmpeg.
    """

    try:
        import imageio_ffmpeg
    except ImportError:
        raise RuntimeError(
            "MTS conversion requires the 'imageio-ffmpeg' package. "
            "Run: pip install -r requirements.txt"
        )

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    fd, output_path = tempfile.mkstemp(
        suffix=".mp4",
        prefix="gemini_converted_",
    )
    os.close(fd)

    command = [
        ffmpeg,
        "-y",
        "-i", video_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        os.unlink(output_path)
        raise RuntimeError(f"ffmpeg failed to start: {exc}")

    if result.returncode != 0:
        os.unlink(output_path)
        raise RuntimeError(
            f"MTS conversion failed:\n{result.stderr[-1000:]}"
        )

    return output_path


def upload_video(video_path):

    source = Path(video_path)

    converted = None

    # ------------------------------------------------
    # Convert unsupported formats (MTS / M2TS / TS)
    # ------------------------------------------------

    if source.suffix.lower() in CONVERT_EXTENSIONS:

        print(f"Converting {source.suffix.upper()} to MP4...")

        converted = convert_to_mp4(str(source))

        video_path = converted

    try:

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

    finally:

        # ------------------------------------------------
        # Delete converted temp file
        # ------------------------------------------------

        if converted and os.path.exists(converted):

            os.unlink(converted)


def delete_gemini_file(file_name):
    """Delete uploaded video from Gemini cloud storage."""
    try:
        client.files.delete(name=file_name)
    except Exception:
        pass
