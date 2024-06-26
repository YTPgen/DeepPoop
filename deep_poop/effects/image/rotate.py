import random

import cv2
import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils
import numpy as np
from deep_poop.clips.cut_clip import FullFrame
from deep_poop.scene import Scene
from face_feature_recognizer.face import Face
from moviepy.editor import VideoClip


class Rotate(effect.ImageEffect):
    """Rotates images in a video.

    Args:
        min_speed (float): Minimum rotations per second
        max_speed (float): Maximum rotations per second

    """

    def __init__(
        self,
        min_speed: float,
        max_speed: float,
        center_on_face: bool = False,
        *args,
        **kwargs
    ):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Rotate, self).__init__(*args, **kwargs)
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.center_on_face = center_on_face
        # TODO: Consider adding scale up/down
        self.scale = 1

    def initialize_effect(self, scene: Scene, strength: float):
        self.speed = (self.max_speed - self.min_speed) * strength + self.min_speed

    def apply_frame(self, frame: FullFrame, scene: Scene, index: int) -> np.ndarray:
        (height, width) = frame.shape[:2]
        if self.center_on_face and len(frame.faces) > 0:
            # TODO: Consider smarter approach for following same face
            focus_face: Face = frame.faces[0]
            center = focus_face.center_of(focus_face.__dict__)
        else:
            center = (width / 2, height / 2)
        angles_per_frame = 360 * self.speed / scene.clip.fps
        angle = angles_per_frame * index
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, self.scale)
        return cv2.warpAffine(frame, rotation_matrix, (width, height))
