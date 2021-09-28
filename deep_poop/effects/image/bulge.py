from deep_poop.analytics.face_detect import face_to_center
from deep_poop.clips.cut_clip import FullFrame
import numpy as np
import math

from deep_poop.scene import Scene
from deep_poop.value_generator import (
    ZERO,
    ConstantValueGenerator,
    RandomValueGenerator,
    ValueGenerator,
)
from deep_poop.effects.interpolator import StrengthInterpolator
import deep_poop.effects.effect as effect


class Bulge(effect.ImageEffect):
    """Swirls a portion of a video.

    Args:
        min_speed (float): Minimum rotations per second
        max_speed (float): Maximum rotations per second

    """

    def __init__(
        self,
        min_bulge: float,
        max_bulge: float,
        interpolator: StrengthInterpolator = StrengthInterpolator(),
        transition_time_generator: ValueGenerator = ZERO,
        radius_generator: ValueGenerator = ConstantValueGenerator(0.1),
        center_on_face: bool = False,
        invert: bool = False,
        *args,
        **kwargs,
    ):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Bulge, self).__init__(*args, **kwargs)
        self.min_bulge = min_bulge
        self.max_bulge = max_bulge
        self.invert = invert
        self.radius_generator = radius_generator
        self.center_on_face = center_on_face
        self.transition_time_generator = transition_time_generator
        self.interpolator = interpolator

    def initialize_effect(self, scene: Scene, strength: float):
        interpolation_multipliers = self.interpolator.interpolate_all_frames(scene)
        self._strengths = [m * strength for m in interpolation_multipliers]

        self._radius = self.radius_generator.generate()
        self._transition_time = self.transition_time_generator.generate()

    def apply_frame(self, frame: np.ndarray, scene: Scene, index: int) -> np.ndarray:
        strength = self._strengths[index]
        current_time = index / scene.frame_length() * scene.length()
        current_scene_frame: FullFrame = scene.frames[index]

        if self._transition_time > 0:
            transition_multiplier = min(1, current_time / self._transition_time)
        else:
            transition_multiplier = 1

        current_bulge = (
            self.min_bulge
            + (self.max_bulge - self.min_bulge) * strength * transition_multiplier
        )

        (height, width) = frame.shape[:2]
        if self.center_on_face:
            if len(current_scene_frame.face_locations) > 0:
                face = current_scene_frame.face_locations[0]
                center = face_to_center(face)
            else:
                return frame
        else:
            center = (width / 2, height / 2)

        center_height = center[1]
        center_width = center[0]
        radius = self._radius * (height if height > width else width)
        dst = frame.copy()

        for y in range(len(frame)):
            v = y - center_height
            if abs(v) > radius:
                continue
            x_start = max(
                0, math.floor(-math.sqrt(radius ** 2 - v ** 2) + center_width)
            )
            x_end = min(
                width, math.ceil(math.sqrt(radius ** 2 - v ** 2) + center_width)
            )
            for x in range(x_start, x_end):
                u = x - center_width
                r = math.sqrt(u ** 2 + v ** 2)
                r = 1 - r / radius
                if r > 0:
                    r2 = 1 - current_bulge * r * r
                    xp = u * r2
                    yp = v * r2

                    src_y = max(0, min(int(yp + center_height), height - 1))
                    src_x = max(0, min(int(xp + center_width), width - 1))

                    dst[y][x] = frame[src_y][src_x]
        return dst


def bulge(image: np.ndarray, strength: float, center: tuple = None) -> np.ndarray:
    """Creates a swelling or deflating effect in an image with a given center.
    Args:
        image (numpy.ndarray): Image to modify
        strength (float): Strength of inflation (can be negative)
        center (tuple, optional): Center of effect (x,y). Defaults to None.
    Returns:
        [type]: [description]
    """
    height, width = image.shape[:2]
    if center is None:
        center = (height // 2, width // 2)

    center_height = center[1]
    center_width = center[0]
    max_radius = min(center_width, center_height)
    dst = image.copy()

    for y in range(len(image)):
        v = y - center_height
        if abs(v) > max_radius:
            continue
        x_start = max(
            0, math.floor(-math.sqrt(max_radius ** 2 - v ** 2) + center_width)
        )
        x_end = min(
            width, math.ceil(math.sqrt(max_radius ** 2 - v ** 2) + center_width)
        )
        for x in range(x_start, x_end):
            u = x - center_width
            r = math.sqrt(u ** 2 + v ** 2)
            r = 1 - r / max_radius
            if r > 0:
                r2 = 1 - strength * r * r
                xp = u * r2
                yp = v * r2

                src_y = max(0, min(int(yp + center_height), height - 1))
                src_x = max(0, min(int(xp + center_width), width - 1))

                dst[y][x] = image[src_y][src_x]
    return dst
