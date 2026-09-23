import os
import re
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

# =========================================================
# SIZE LIMITS
# =========================================================

# The Gemini Files API refuses any single file above 2 GB, so anything
# larger has to be re-encoded down before it is sent.
GEMINI_MAX_BYTES = 2 * 1024 * 1024 * 1024

# Aim under the hard cap: x264 rate control overshoots a little and the
# MP4 container adds its own overhead.
COMPRESS_TARGET_BYTES = int(1.80 * 1024 * 1024 * 1024)

# Downscale anything wider than this. 720p still shows operators, hands
# and parts clearly, which is all the time study needs.
MAX_WIDTH = 1280

AUDIO_BITRATE_BPS = 128_000

# Below this the picture stops being readable, so a video long enough to
# need it is rejected instead of encoded into mush.
MIN_VIDEO_BITRATE_BPS = 300_000


def _ffmpeg_exe():
    """Path to the ffmpeg binary bundled with imageio-ffmpeg."""

    try:
        import imageio_ffmpeg
    except ImportError:
        raise RuntimeError(
            "Video conversion requires the 'imageio-ffmpeg' package. "
            "Run: pip install -r requirements.txt"
        )

    return imageio_ffmpeg.get_ffmpeg_exe()


_DURATION_PATTERN = re.compile(r"Duration:\s*(\d+):(\d\d):(\d\d(?:\.\d+)?)")


def _probe_duration(video_path):
    """
    Duration of the video in seconds, or None if it cannot be read.

    imageio-ffmpeg ships ffmpeg but no ffprobe, so the stream header that
    ffmpeg prints on stderr is the only probe available here.
    """

    try:
        result = subprocess.run(
            [_ffmpeg_exe(), "-hide_banner", "-i", str(video_path)],
            capture_output=True,
            text=True,
        )
    except Exception:
        return None

    # ffmpeg exits non-zero because no output file was given, but it
    # prints the header we want before giving up.
    match = _DURATION_PATTERN.search(result.stderr or "")

    if not match:
        return None

    hours, minutes, seconds = match.groups()

    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


# ffmpeg reports both keys in microseconds - "out_time_ms" is a
# long-standing misnomer in ffmpeg's own progress output, so dividing it
# by 1000 would report 100% on every tick.
_PROGRESS_PATTERN = re.compile(r"out_time_(?:us|ms)=(\d+)")


def _run_ffmpeg(command, total_seconds=None, on_progress=None, action=""):
    """
    Run ffmpeg and forward encode progress as a 0.0 - 1.0 fraction.

    stderr is kept quiet with -nostats / -loglevel error so it cannot
    fill its pipe buffer and deadlock while stdout is being read.
    """

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    for line in process.stdout:

        if on_progress is None or not total_seconds:
            continue

        match = _PROGRESS_PATTERN.match(line.strip())

        if match:
            done = int(match.group(1)) / 1_000_000
            on_progress(min(done / total_seconds, 1.0), action)

    process.stdout.close()

    stderr = process.stderr.read()
    process.stderr.close()

    if process.wait() != 0:
        raise RuntimeError(f"ffmpeg failed:\n{stderr[-1000:]}")


def prepare_for_gemini(video_path, on_progress=None):
    """
    Convert and / or shrink a video until the Gemini Files API accepts it.

    Returns the path of a new temp file the caller must delete, or None
    when the original file can be uploaded untouched.
    """

    source = Path(video_path)

    needs_convert = source.suffix.lower() in CONVERT_EXTENSIONS
    needs_compress = source.stat().st_size > GEMINI_MAX_BYTES

    if not needs_convert and not needs_compress:
        return None

    action = "Compressing" if needs_compress else "Converting"

    duration = _probe_duration(source)

    command = [
        _ffmpeg_exe(),
        "-y",
        "-nostats",
        "-loglevel", "error",
        "-progress", "pipe:1",
        "-i", str(source),
    ]

    if needs_compress:

        if not duration:
            raise RuntimeError(
                "Could not read this video's duration, so it cannot be "
                "compressed automatically. Please compress or trim it "
                "below 2 GB and upload again."
            )

        # Spread the byte budget evenly over the running time and cap the
        # peak, so the encode lands under Gemini's limit predictably.
        total_bps = int(COMPRESS_TARGET_BYTES * 8 / duration)
        video_bps = total_bps - AUDIO_BITRATE_BPS

        if video_bps < MIN_VIDEO_BITRATE_BPS:
            hours = duration / 3600
            raise RuntimeError(
                f"This video is {hours:.1f} hours long, which cannot be "
                "compressed under Gemini's 2 GB limit without destroying "
                "the picture. Please split it into shorter segments and "
                "analyse them one at a time."
            )

        command += [
            "-vf", f"scale='min({MAX_WIDTH},iw)':-2",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-b:v", str(video_bps),
            "-maxrate", str(video_bps),
            "-bufsize", str(video_bps * 2),
            "-pix_fmt", "yuv420p",
        ]

    else:
        # Container / codec change only (MTS, AVCHD). Quality target, no
        # size cap, because the file already fits.
        command += [
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
        ]

    fd, output_path = tempfile.mkstemp(
        suffix=".mp4",
        prefix="gemini_prepared_",
    )
    os.close(fd)

    command += [
        "-c:a", "aac",
        "-b:a", f"{AUDIO_BITRATE_BPS // 1000}k",
        "-movflags", "+faststart",
        output_path,
    ]

    print(f"{action} {source.name} for upload...")

    try:
        _run_ffmpeg(command, duration, on_progress, action)
    except Exception:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise

    # Safety net: rate control can still overshoot on unusual footage.
    if os.path.getsize(output_path) > GEMINI_MAX_BYTES:
        os.unlink(output_path)
        raise RuntimeError(
            "The compressed video is still above Gemini's 2 GB limit. "
            "Please split it into shorter segments and analyse them one "
            "at a time."
        )

    return output_path


def convert_to_mp4(video_path):
    """
    Convert an unsupported video (e.g. .MTS / AVCHD) to .mp4.

    Kept as a thin wrapper around prepare_for_gemini for callers that
    only want the container change.
    """

    return prepare_for_gemini(video_path) or str(video_path)


def upload_video(video_path, on_progress=None):

    # ------------------------------------------------
    # Convert unsupported formats (MTS / M2TS / TS) and
    # shrink anything above Gemini's 2 GB per-file cap
    # ------------------------------------------------

    prepared = prepare_for_gemini(video_path, on_progress=on_progress)

    upload_path = prepared or str(video_path)

    try:

        file = client.files.upload(
            file=upload_path
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
        # Delete the prepared temp file
        # ------------------------------------------------

        if prepared and os.path.exists(prepared):

            os.unlink(prepared)


def delete_gemini_file(file_name):
    """Delete uploaded video from Gemini cloud storage."""
    try:
        client.files.delete(name=file_name)
    except Exception:
        pass
