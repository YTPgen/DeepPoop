import numpy as np

from moviepy.editor import VideoClip
import cv2

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils


class Pixelate(effect.ImageEffect):
    """Pixelates images in a video.

    Args:
        speed (float): Rotations per second

    """

    def __init__(self, speed: float, center_on_face: bool = False, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Pixelate, self).__init__(*args, **kwargs)
        self.speed = speed
        self.center_on_face = center_on_face
        # TODO: Consider adding scale up/down
        self.scale = 1

    def initialize_effect(self):
        self.angle = 0

    def apply_frame(self, frame: np.ndarray):
        (height, width) = frame.shape[:2]
        if self.center_on_face:
            # TODO: Implement
            raise NotImplementedError
        else:
            center = (width / 2, height / 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, self.angle, self.scale)
        return cv2.warpAffine(frame, rotation_matrix, (width, height))
