import numpy as np

from moviepy.editor import VideoClip
import cv2

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils


class Invert(effect.ImageEffect):
    """Inverts images in a video.

    """

    def __init__(self, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Invert, self).__init__(*args, **kwargs)

    def apply_frame(self, frame: np.ndarray):
        return cv2.bitwise_not(frame)
