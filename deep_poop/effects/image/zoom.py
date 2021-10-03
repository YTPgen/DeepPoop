from deep_poop.analytics.face_detect import face_to_center
from deep_poop.clips.cut_clip import FullFrame
import numpy as np

from moviepy.editor import VideoClip
import cv2

import deep_poop.effects.effect as effect
from deep_poop.effects.interpolator import StrengthInterpolator
from deep_poop.scene import Scene


class Zoom(effect.ImageEffect):
    """Zooms in on a location in an image.

    Args:
        min_factor (float): Minimum zoom factor
        max_factor (float): Maximum zoom factor
        center_on_face (bool): Whether zoom should center on a face in frame (False by default)
        zoom_x (bool): Whether zoom should work on X axis (True by default)
        zoom_y (bool): Whether zoom should work on Y axis (True by default)
    """

    def __init__(
        self,
        min_factor: int,
        max_factor: int,
        interpolator: StrengthInterpolator = StrengthInterpolator(),
        center_on_face: bool = False,
        zoom_x: bool = True,
        zoom_y: bool = True,
        *args,
        **kwargs,
    ):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Zoom, self).__init__(*args, **kwargs)
        self.min_factor = min_factor
        self.max_factor = max_factor
        self.center_on_face = center_on_face
        self.zoom_x = zoom_x
        self.zoom_y = zoom_y
        self.interpolator = interpolator

    def initialize_effect(self, scene: Scene, strength: float):
        self.interpolation_multipliers = self.interpolator.interpolate_all_frames(scene)

        self.factor_x = (
            (self.max_factor - self.min_factor) * strength + self.min_factor
            if self.zoom_x
            else 1
        )
        self.factor_y = (
            (self.max_factor - self.min_factor) * strength + self.min_factor
            if self.zoom_y
            else 1
        )
        self._last_center = None

    def apply_frame(self, frame: np.ndarray, scene: Scene, index: int):
        increment_per_frame = 1 / (scene.length() * scene.clip.fps)
        current_factor_x = 1 + index * increment_per_frame * (self.factor_x - 1)
        current_factor_y = 1 + index * increment_per_frame * (self.factor_y - 1)
        (height, width) = frame.shape[:2]

        interpolation_multiplier = self.interpolation_multipliers[index]
        scaled = cv2.resize(
            frame,
            None,
            fx=current_factor_x * interpolation_multiplier,
            fy=current_factor_y * interpolation_multiplier,
            interpolation=cv2.INTER_LINEAR,
        )

        center = self.get_center(scene.frames[index])
        center = (
            center[1] * current_factor_y,
            center[0] * current_factor_x,
        )

        crop_from_y = int(max(0, center[0] - height / 2))
        crop_to_y = int(min(height * current_factor_y, crop_from_y + height))

        crop_from_x = int(max(0, center[1] - width / 2))
        crop_to_x = int(min(width * current_factor_x, crop_from_x + width))
        cropped = scaled[crop_from_y:crop_to_y, crop_from_x:crop_to_x]

        # If image is smaller than before, pad with black
        if cropped.shape[0] < height or cropped.shape[1] < width:
            y_pad = max(0, height - cropped.shape[0])
            x_pad = max(0, width - cropped.shape[1])
            return cv2.copyMakeBorder(
                cropped,
                y_pad // 2,
                y_pad - y_pad // 2,
                x_pad // 2,
                x_pad - x_pad // 2,
                cv2.BORDER_CONSTANT,
                value=[0, 0, 0],
            )

        return cropped

    def get_center(self, current_frame: FullFrame):
        (height, width) = current_frame.video_frame.shape[:2]
        if self.center_on_face:
            if len(current_frame.face_locations) > 0:
                face = current_frame.face_locations[0]
                return face_to_center(face)
            elif self._last_center is not None:
                return self._last_center
        return (width // 2, height // 2)
