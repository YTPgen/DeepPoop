from typing import List


class Scene:
    """Metadata about a scene in a video.

    Args:
        video_file (str): Filename of video file scene is in
        start (float): Start frame of scene
        end (float): End frame of scene
        subscenes (List[Scene], optional): List of subscenes in scene. Defaults to empty list.
    """

    def __init__(
        self, video_file: str, start: float, end: float, subscenes: "List[Scene]" = []
    ):
        self.video_file = video_file
        self.start = start
        self.end = end
        self.subscenes = subscenes

    def length(self):
        return self.end - self.start
