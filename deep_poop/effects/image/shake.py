import numpy as np
import random

from moviepy.editor import VideoClip
import cv2
from face_feature_recognizer.face import Face

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils
from deep_poop.clips.cut_clip import FullFrame
from deep_poop.scene import Scene


class Shake(effect.ImageEffect):
    """Translates images in a video to produce a shake effect.

    Args:
        min_strength (float): Minimum strength of shaking effect
        max_strength (float): Maximum strength of shaking effect

    """

    def __init__(self, min_strength: float, max_strength: float, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Shake, self).__init__(*args, **kwargs)
        self.min_strength = min_strength
        self.max_strength = max_strength

    def initialize_effect(self, scene: Scene, strength: float):
        self.shake_strength = (
            self.min_strength - self.max_strength
        ) * strength + self.min_strength

    def apply_frame(self, frame: FullFrame, scene: Scene, index: int) -> np.ndarray:
        by_x = random.uniform(-self.shake_strength, self.shake_strength)
        by_y = random.uniform(-self.shake_strength, self.shake_strength)
        T = np.float32([[1, 0, by_x], [0, 1, by_y]])
        return cv2.warpAffine(frame, T, (frame.shape[1], frame.shape[0]))
