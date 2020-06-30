import numpy as np
from enum import Enum
import random
import abc

import cv2
from moviepy.editor import VideoClip, ImageSequenceClip


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
        print("Warning: Defaulting to random effect length")
        return random.uniform(min_len, max_len)

    def apply(self, video: VideoClip):
        self.initialize_effect()
        self.effect_function(video)

    @abc.abstractmethod
    def effect_function(self, video: VideoClip):
        """Functionality when effect is applied. To be implemented by each effect.

        Args:
            video (VideoClip): Video to apply effect on
        """
        raise NotImplementedError


class ImageEffect(Effect):
    def __init__(self, *args, **kwargs):
        super(ImageEffect, self).__init__(*args, **kwargs)

    def effect_function(self, video: VideoClip):
        output_frames = []
        for t, video_frame in video.iter_frames(with_times=True):
            video_frame = cv2.cvtColor(video_frame, cv2.COLOR_RGB2BGR)
            f = self.apply_frame(video_frame)
            output_frames.append(f)
        output_video = ImageSequenceClip(output_frames, video.fps)
        output_video.audio = video.audio
        return output_video

    @abc.abstractmethod
    def apply_frame(self, frame: np.ndarray):
        pass


# effects = [
#     ImageEffect(
#         name="invert",
#         function=ytp_effects.image.color.invert,
#         intensity=1.5,
#         effect_type=EffectType.IMAGE,
#         max_len=2.5,
#         length_distribution=EffectLengthDistribution.RANDOM,
#     ),
# ]

