from typing import List

from moviepy.editor import VideoFileClip, VideoClip
from face_feature_recognizer.face_feature_recognizer import FaceFeatureRecognizer

from deep_poop.clips.cut_clip import FullFrame, CutClip
from deep_poop.config import using_gpu, skip_faces


class Scene:
    """Metadata about a scene in a video.

    Args:
        video_file (str): Filename of video file scene is in
        start (float): Start frame of scene
        end (float): End frame of scene
        subscenes (List[Scene], optional): List of subscenes in scene. Defaults to empty list.
    """

    def __init__(
        self, video_file: str, start: float, end: float, subscenes: "List[Scene]" = [],
    ):
        self.video_file = video_file
        self.start = start
        self.end = end
        self.subscenes = subscenes
        self.clip: VideoClip = self._get_scene_clip()

    def _get_scene_clip(self):
        video: VideoClip = VideoFileClip(self.video_file)
        return video.subclip(self.start / video.fps, self.end / video.fps)

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
        return self.frame_length() / self.clip.fps

    def frame_length(self) -> int:
        """Gets amount of frames in scene

        Returns:
            int: Amount of frames in scene
        """
        return self.end - self.start

    def copy(self):
        """Returns a copy of this scene

        Returns:
            Scene: Distinct copy of scene
        """
        scene_copy = Scene(video_file=self.video_file, start=self.start, end=self.end)
        scene_copy.frames = self.frames
        return scene_copy

    def subclip(self, start, end):
        start = int(start)
        end = int(end)
        new_frames = self.frames[start - self.start : end - self.start]
        if len(new_frames) == 0:
            print("Uhoh")
        self.frames = new_frames
        self.start = start
        self.end = end
        self.clip: VideoClip = self._get_scene_clip()
        return self
