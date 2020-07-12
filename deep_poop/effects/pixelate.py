import numpy as np

from moviepy.editor import VideoClip
import cv2

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils
from deep_poop.scene import Scene


class Pixelate(effect.ImageEffect):
    """Pixelates images in a video.

    Args:
        min_strength (float): Minimum amount of pixelation
        max_strength (float): Maximum amount of pixelation
    """

    def __init__(self, min_strength: int, max_strength: int, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Pixelate, self).__init__(*args, **kwargs)
        self.min_strength = min_strength
        self.max_strength = max_strength

    def initialize_effect(self, strength: float):
        self.angle = 0
        self.strength = (
            self.max_strength - self.min_strength
        ) * strength + self.min_strength

    def apply_frame(self, frame: np.ndarray, scene: Scene):
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
