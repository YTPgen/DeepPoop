from typing import List
import math
import os
import pickle

from moviepy.editor import VideoFileClip, VideoClip
from face_feature_recognizer.face_feature_recognizer import FaceFeatureRecognizer

from deep_poop.clips.cut_clip import FullFrame, CutClip
from deep_poop.config import using_gpu, skip_faces
from deep_poop.analytics.face_detect import (
    face_locations,
    batch_face_locations,
)


class VideoCache:
    """Helper class for storing cached information of a video

    Args:
        video_clip (VideoClip): Video clip of scene
    """

    def __init__(
        self,
        file: str,
        frames: List[FullFrame],
    ):
        self.frames = frames
        self.file = file

    @classmethod
    def from_file(cls, cache_file: str):
        if not os.path.exists(cache_file):
            return None
        with open(cache_file, "rb") as f:
            return pickle.load(f)

    def write(self, from_frame: int, frames: List[FullFrame]):
        self.frames[from_frame : from_frame + len(frames)] = frames
        with open(self.file, "wb") as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def read(self, from_frame: int, to_frame: int) -> List[FullFrame]:
        return self.frames[from_frame:to_frame]


class Scene:
    """Metadata about a scene in a video.

    Args:
        video_clip (VideoClip): Video clip of scene
        start_frame_index (int): Global index of where the first frame of this scene is in original video
        subscenes (List[Scene], optional): List of subscenes in scene. Defaults to empty list.
    """

    def __init__(
        self,
        video_clip: VideoClip,
        start_frame_index: int,
        subscenes: "List[Scene]" = [],
        cache: VideoCache = None,
    ):
        self.subscenes = subscenes
        self.clip = video_clip
        self.cache = cache
        self.start_frame_index = start_frame_index
        if cache is None:
            self.frames = [None] * self.frame_length()
        else:
            self.frames = self.cache.read(self.start_frame_index, self.end_frame_index)

    @property
    def end_frame_index(self):
        return self.start_frame_index + self.frame_length()

    def enable_cache(self, cache_file: str):
        cache = VideoCache.from_file(cache_file)
        if cache is None:
            cache = VideoCache(cache_file, self.frames)
        else:
            cached_frames = cache.read(self.start_frame_index, self.end_frame_index)
            if len(cached_frames) == self.frame_length():
                self.frames = cached_frames
            else:
                print(
                    f"WARNING: Cached file {cache_file} contained invalid amount of frames. Skipping cache..."
                )
        self.cache = cache

    def analyze_frames(self, keep_face_for_frames: int = 3) -> List[FullFrame]:
        """Analyzes each frame of scene clip for metadata"""
        video_frames: List[FullFrame] = CutClip(self.clip).frames
        frames_to_analyze = []
        for i, frame in enumerate(self.frames):
            if frame is None:
                frames_to_analyze.append((i, video_frames[i]))

        if not skip_faces():
            image_frames = []
            for i in range(len(frames_to_analyze)):
                if i % keep_face_for_frames == 0:
                    image_frames.append(frames_to_analyze[i][1].video_frame)
            if using_gpu():
                frames_face_locations = batch_face_locations(
                    image_frames, batch_size=16
                )
            else:
                frames_face_locations = [
                    face_locations(f.video_frame) for f in image_frames
                ]
            for i in range(len(frames_to_analyze)):
                if i % keep_face_for_frames != 0:
                    frames_face_locations.insert(i, frames_face_locations[i - 1])
            for frame, faces in zip(frames_to_analyze, frames_face_locations):
                index = frame[0]
                video_frames[index].face_locations = faces
                self.frames[index] = video_frames[index]
        self.cache.write(self.start_frame_index, self.frames)

    def has_faces(self) -> bool:
        return self.faces_amount() > 0

    def faces_amount(self) -> int:
        return max([len(f.face_locations) for f in self.frames])

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
        subscene = Scene(
            start_frame_index=self.start_frame_index + start_frame,
            video_clip=self.clip.subclip(start, end),
            cache=self.cache,
        )
        # Hack to disable close as clip would close io reader on deletion
        subscene.clip.close = lambda *args: None
        subscene.frames = self.frames[start_frame:end_frame]
        return subscene
