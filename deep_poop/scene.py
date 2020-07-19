from typing import List
import math

from moviepy.editor import VideoFileClip, VideoClip
from face_feature_recognizer.face_feature_recognizer import FaceFeatureRecognizer

from deep_poop.clips.cut_clip import FullFrame, CutClip
from deep_poop.config import using_gpu, skip_faces


class Scene:
    """Metadata about a scene in a video.

    Args:
        video_clip (VideoClip): Video clip of scene
        subscenes (List[Scene], optional): List of subscenes in scene. Defaults to empty list.
    """

    def __init__(
        self, video_clip: VideoClip, subscenes: "List[Scene]" = [],
    ):
        self.subscenes = subscenes
        self.clip = video_clip
        self.frames = []

    def analyze_frames(self) -> List[FullFrame]:
        """Analyzes each frame of scene clip for metadata 

        """
        frames: List[FullFrame] = CutClip(self.clip).frames
        if not skip_faces():
            if using_gpu:
                image_frames = [f.video_frame for f in frames]
                frames_face_locations = FaceFeatureRecognizer.batch_face_locations(
                    image_frames, batch_size=128
                )
            else:
                frames_face_locations = [
                    FaceFeatureRecognizer.face_locations(f.video_frame) for f in frames
                ]
            for frame, face_locations in zip(frames, frames_face_locations):
                frame.face_locations = face_locations
        self.frames = frames

    def has_faces(self):
        return self.faces_amount() > 0

    def faces_amount(self):
        return max([len(f.faces) for f in self.frames])

    def length(self) -> float:
        """Gets length of scene in seconds

        Returns:
            float: Length of scene in seconds
        """
        return self.clip.duration

    def frame_length(self) -> int:
        """Gets amount of frames in scene

        Returns:
            int: Amount of frames in scene
        """
        return math.ceil(self.clip.duration * self.clip.fps)

    def subscene(self, start: float, end: float):
        """Returns a subscene of this scene with shorter or equal clip duration.

        Args:
            start (float): Start offset in seconds
            end (float): End time of scene in seconds

        Returns:
            Scene: Subscene of this scene 
        """
        end = max(min(self.clip.duration, end), 1 / self.clip.fps)
        start = min(max(0, start), end - 1 / self.clip.fps)
        start_frame = int(round(start * self.clip.fps))
        end_frame = int(round(end * self.clip.fps))
        subscene = Scene(video_clip=self.clip.subclip(start, end))
        # Hack to disable close as clip would close io reader on deletion
        subscene.clip.close = lambda *args: None
        subscene.frames = self.frames[start_frame:end_frame]
        return subscene
