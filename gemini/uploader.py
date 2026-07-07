import time

from .config import client


def upload_video(video_path):

    file = client.files.upload(
        file=video_path
    )

    while file.state.name == "PROCESSING":

        time.sleep(5)

        file = client.files.get(
            name=file.name
        )

    return file