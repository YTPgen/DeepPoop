from skimage.transform import swirl
import numpy as np

import deep_poop.effects.effect as effect
from deep_poop.analytics.face_detect import face_to_center
from deep_poop.clips.cut_clip import FullFrame
from deep_poop.effects.interpolator import StrengthInterpolator
from deep_poop.scene import Scene
from deep_poop.value_generator import ZERO, ConstantValueGenerator, ValueGenerator


class Swirl(effect.ImageEffect):
    """Swirls a portion of a video.

    Args:
        min_speed (float): Minimum rotations per second
        max_speed (float): Maximum rotations per second

    """

    def __init__(
        self,
        min_swirl: float,
        max_swirl: float,
        interpolator: StrengthInterpolator = StrengthInterpolator(),
        transition_time_generator: ValueGenerator = ZERO,
        radius_generator: ValueGenerator = ConstantValueGenerator(0.1),
        center_on_face: bool = False,
        *args,
        **kwargs
    ):
        kwargs["effect_type"] = effect.EffectType.IMAGE
        super(Swirl, self).__init__(*args, **kwargs)
        self.min_swirl = min_swirl
        self.max_swirl = max_swirl
        self.radius_generator = radius_generator
        self.center_on_face = center_on_face
        self.transition_time_generator = transition_time_generator
        self.interpolator = interpolator

    def selection_score(self, scene: Scene) -> float:
        if self.center_on_face:
            return 1 if scene.faces_amount() > 0 else 0
        return 0.5

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
            swirl_transition = min(1, current_time / self._transition_time)
        else:
            swirl_transition = 1

        current_swirl_amount = (
            self.min_swirl
            + (self.max_swirl - self.min_swirl) * strength * swirl_transition
        )

        (height, width) = frame.shape[:2]
        if self.center_on_face:
            if len(current_scene_frame.face_locations) > 0:
                face = current_scene_frame.face_locations[0]
                center = face_to_center(face)
            else:
                return frame
        else:
            center = (width // 2, height // 2)

        radius = self._radius * (height if height > width else width)

        return (
            swirl(
                frame,
                center,
                strength=current_swirl_amount,
                radius=radius,
            )
            * 255
        )
