import numpy as np

from moviepy.editor import VideoClip
import cv2

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils


class Pixelate(effect.ImageEffect):
    """Pixelates images in a video.

    Args:
        strength (float): Amount of pixelation

    """

    def __init__(self, strength: float, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Pixelate, self).__init__(*args, **kwargs)
        self.strength = strength

    def apply_frame(self, frame: np.ndarray):
        squish_strength = 1 + self.strength
        (height, width) = frame.shape[:2]
        frame = cv2.resize(
            frame,
            (int(width / squish_strength), int(height / squish_strength)),
            interpolation=cv2.INTER_NEAREST,
        )
        return cv2.resize(
            frame, (int(width), int(height)), interpolation=cv2.INTER_LINEAR,
        )
