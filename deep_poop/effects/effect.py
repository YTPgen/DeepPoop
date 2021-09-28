import math
import operator
import functools
import multiprocessing
import numpy as np
from enum import Enum
import random
import abc

import cv2
from moviepy.editor import VideoClip, ImageSequenceClip

from deep_poop.scene import Scene


class EffectStrengthCurve(Enum):
    FLAT = 0
    IMAGE = 1
    VIDEO = 2


class EffectType(Enum):
    AUDIO = 0
    IMAGE = 1
    VIDEO = 2


class EffectLengthDistribution(Enum):
    RANDOM = 0
    NORMAL = 1


class Effect:
    def __init__(
        self,
        intensity: float,
        effect_type: EffectType,
        min_len: float = 0.5,
        max_len: float = 3600,
        length_distribution: EffectLengthDistribution = None,
        can_cut: bool = False,
        standalone=True,
        name=None,
    ):
        self.intensity = intensity
        self.type = effect_type
        self.min_len = min_len
        self.max_len = max_len
        self.can_cut = can_cut
        self.length_distribution = length_distribution
        self.standalone = standalone
        self.name = self.__class__.__name__ if name is None else name

    def initialize_effect(self, scene: Scene, strength: float):
        """Any initialization that needs to take place when effect is used."""
        pass

    def effect_length(self, max_len: float):
        max_len = min(self.max_len, max_len)
        min_len = self.min_len
        if self.length_distribution == EffectLengthDistribution.RANDOM:
            length = random.uniform(min_len, max_len)
        elif self.length_distribution == EffectLengthDistribution.NORMAL:
            middle = (max_len + min_len) / 2
            sigma = (max_len - middle) / 10
            length = random.gauss((max_len + min_len) / 2, sigma)
        else:
            # TODO: Log
            # print("Warning: Defaulting to random effect length")
            length = random.uniform(min_len, max_len)
        if length <= 0:
            raise ValueError
        return length

    def apply(self, scene: Scene, workers: int = 1, strength: int = 1):
        self.initialize_effect(scene, strength)
        changed_clip = self.effect_function(scene, workers)
        return changed_clip

    def selection_score(self, scene: Scene) -> float:
        """Returns a score for how well this effect matches a given scene.
        For example, a score of 0 is no match at all and a score of 1 is a full match.

        Args:
            scene (Scene): Scene to find selection score for

        Returns:
            float: Selection score
        """
        return 0.5

    @abc.abstractmethod
    def effect_function(self, scene: Scene) -> VideoClip:
        """Functionality when effect is applied. To be implemented by each effect.

        Args:
            scene (Scene): Scene to apply effect on

        Returns:
            VideoClip: Scene video clip with applied function
        """
        raise NotImplementedError


class ImageEffect(Effect):
    def __init__(self, *args, **kwargs):
        super(ImageEffect, self).__init__(*args, **kwargs)

    def effect_function(self, scene: Scene, workers: int) -> VideoClip:
        """Applies image effect to each frame of scene video clip.

        Args:
            scene (Scene): Scene to apply effect on

        Returns:
            VideoClip: Transformed scene video clip
        """
        output_frames = []
        if workers > 1:
            output_frames = self._parallel_apply(scene)
        else:
            for i, frame in enumerate(scene.frames):
                f = self.apply_frame(frame.video_frame, scene, i)
                output_frames.append(f)
        output_video = ImageSequenceClip(output_frames, scene.clip.fps)
        output_video.audio = scene.clip.audio.copy()
        return output_video

    def _parallel_apply(self, scene: Scene, workers: int):
        manager = multiprocessing.Manager()
        result_list = manager.list()
        for i in range(self.workers):
            result_list.append([])
        jobs = []

        def _apply_frame_parallel(worker_index, frames, frames_start_index):
            processed_frames = []
            i = frames_start_index
            for frame in frames:
                f = self.apply_frame(frame.video_frame, scene, i)
                processed_frames.append(f)
                i += 1
            result_list[worker_index] = processed_frames

        frames_per_worker = math.ceil(scene.frame_length() / workers)
        for i in range(self.workers):
            worker_start = i * frames_per_worker
            frames = scene.frames[worker_start : worker_start + frames_per_worker]
            p = multiprocessing.Process(
                target=_apply_frame_parallel,
                args=(
                    i,
                    frames,
                    worker_start,
                ),
            )
            jobs.append(p)
            p.start()

        for proc in jobs:
            proc.join()
        return functools.reduce(operator.iconcat, result_list, [])

    @abc.abstractmethod
    def apply_frame(self, frame: np.ndarray, scene: Scene, index: int) -> np.ndarray:
        """Applies effect function on a single image frame.

        Args:
            frame (np.ndarray): Image frame
            scene (Scene): Scene info of image frame

        Returns:
            np.ndarray: Transformed image frame
        """
        pass
