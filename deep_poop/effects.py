import numpy as np
from enum import Enum
import random
import cv2

from moviepy.editor import VideoClip, ImageSequenceClip

import ytp_effects


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
        name: str,
        function: "function",
        intensity: float,
        effect_type: EffectType,
        min_len: float = 0,
        max_len: float = 3600,
        length_distribution: EffectLengthDistribution = None,
        can_cut: bool = False,
    ):
        self.name = name
        self.effect_function = function
        self.intensity = intensity
        self.type = effect_type
        self.min_len = min_len
        self.max_len = max_len
        self.can_cut = can_cut
        self.length_distribution = length_distribution

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
        return self.effect_function(video)


class ImageEffect(Effect):
    def __init__(self, *args, **kwargs):
        super(ImageEffect, self).__init__(**kwargs)

    def apply(self, video: VideoClip):
        output_frames = []
        for t, video_frame in video.iter_frames(with_times=True):
            video_frame = cv2.cvtColor(video_frame, cv2.COLOR_RGB2BGR)
            f = self.apply_frame(video_frame)
            output_frames.append(f)
        output_video = ImageSequenceClip(output_frames, video.fps)
        output_video.audio = video.audio
        return output_video

    def apply_frame(self, frame: np.ndarray):
        return self.effect_function(frame)


effects = [
    Effect(
        name="scramble",
        function=ytp_effects.video.scramble.scramble,
        intensity=400,
        effect_type=EffectType.VIDEO,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=True,
    ),
    ImageEffect(
        name="invert",
        function=ytp_effects.image.color.invert,
        intensity=1,
        effect_type=EffectType.IMAGE,
        max_len=2.5,
        length_distribution=EffectLengthDistribution.RANDOM,
    ),
]

