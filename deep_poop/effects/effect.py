import numpy as np
from enum import Enum
import random
import abc

import cv2
from moviepy.editor import VideoClip, ImageSequenceClip

from deep_poop.scene import Scene


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
        min_len: float = 0,
        max_len: float = 3600,
        length_distribution: EffectLengthDistribution = None,
        can_cut: bool = False,
    ):
        self.intensity = intensity
        self.type = effect_type
        self.min_len = min_len
        self.max_len = max_len
        self.can_cut = can_cut
        self.length_distribution = length_distribution

    def initialize_effect(self):
        """Any initialization that needs to take place when effect is used.
        """
        pass

    def effect_length(self, max_len: float):
        max_len = min(self.max_len, max_len)
        min_len = self.min_len
        if self.length_distribution == EffectLengthDistribution.RANDOM:
            return random.uniform(min_len, max_len)
        elif self.length_distribution == EffectLengthDistribution.NORMAL:
            middle = (max_len + min_len) / 2
            sigma = (max_len - middle) / 10
            return random.gauss((max_len + min_len) / 2, sigma)
        # TODO: Log
        # print("Warning: Defaulting to random effect length")
        return random.uniform(min_len, max_len)

    def apply(self, scene: Scene):
        self.initialize_effect()
        original_clip = scene.clip.copy()
        changed_clip = self.effect_function(scene)
        scene.clip = original_clip
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

    def effect_function(self, scene: Scene) -> VideoClip:
        """Applies image effect to each frame of scene video clip.

        Args:
            scene (Scene): Scene to apply effect on

        Returns:
            VideoClip: Transformed scene video clip
        """
        output_frames = []
        for frame in scene.frames:
            # TODO: Fix color or move to FullFrame
            # frame.video_frame = cv2.cvtColor(frame.video_frame, cv2.COLOR_RGB2BGR)
            f = self.apply_frame(frame.video_frame, scene)
            output_frames.append(f)
        output_video = ImageSequenceClip(output_frames, scene.clip.fps)
        output_video.audio = scene.clip.audio
        return output_video

    @abc.abstractmethod
    def apply_frame(self, frame: np.ndarray, scene: Scene) -> np.ndarray:
        """Applies effect function on a single image frame.

        Args:
            frame (np.ndarray): Image frame
            scene (Scene): Scene info of image frame

        Returns:
            np.ndarray: Transformed image frame
        """
        pass
