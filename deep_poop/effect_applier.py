from typing import List
import random
import copy
import numpy as np
import math

from moviepy.editor import VideoClip, concatenate_videoclips

from deep_poop.scene import Scene
from deep_poop.effects.effect import Effect
from deep_poop.config import SELECTION_SCORE_WEIGHT, NEIGHBOR_SCORE_WEIGHT

# TODO: Move to conf
A = -1 / 400
B = -1 / 20


class EffectApplier:
    def __init__(
        self,
        max_intensity: float,
        effects: List[Effect],
        easy_start: float = 0,
        min_effect_length: float = 1.0,
    ):
        self.intensity = easy_start
        self.max_intensity = max_intensity
        self.effects = effects
        self.min_effect_length = min_effect_length
        self._currenty_applied_effects = []
        self._next_effect_intensity_threshold = max(1 - easy_start, 0)

    def _set_next_effect_trigger_threshold(self):
        self._next_effect_intensity_threshold = random.random()

    def _time_until_next_effect(self):
        current_point = self._intensity_to_time(self.intensity)
        target_point = self._intensity_to_time(self._next_effect_intensity_threshold)
        return target_point - current_point

    def _previous_effect(self):
        if len(self._currenty_applied_effects) == 0:
            return None
        return self._currenty_applied_effects[-1]

    def _continue_add_effects(self):
        if (
            self._previous_effect() is not None
            and not self._previous_effect().standalone
            and len(self._currenty_applied_effects) == 1
        ):
            return True
        return self.intensity < self.max_intensity

    def _time_to_intensity(self, time: float) -> float:
        return (time ** 2) * A + time * B

    def _intensity_to_time(self, intensity: float) -> float:
        if intensity > self.max_intensity:
            return -1
        r = B ** 2 - 4 * A * (1 - intensity / self.max_intensity)
        return ((-B) - math.sqrt(r)) / (2 * A)

    def _intensity_loss(self, time: float) -> float:
        """Calculates the total intensity loss over a period of time from current point since last effect

        Args:
            time (float): Time elapsed

        Returns:
            float: Intensity lost
        """
        x1 = max(self._intensity_to_time(self.intensity), 0)
        x2 = x1 + time
        return self.intensity - self._time_to_intensity(x2) * self.max_intensity

    def feed_scene(self, scene: Scene) -> VideoClip:
        _time_until_next_effect = self._time_until_next_effect()
        if (
            _time_until_next_effect > 0
            and _time_until_next_effect > scene.length() - self.min_effect_length
        ):
            self.intensity -= self._intensity_loss(scene.length())
            return scene.clip
        edited_scene = scene.copy()
        self._set_next_effect_trigger_threshold()
        if _time_until_next_effect > 0:
            edited_scene.subclip(
                start=edited_scene.start
                + edited_scene.clip.fps * _time_until_next_effect,
                end=edited_scene.end,
            )
            self._process_scene_effects(edited_scene)
            return concatenate_videoclips(
                [scene.clip.subclip(0, _time_until_next_effect), edited_scene.clip]
            )
        else:
            self._process_scene_effects(edited_scene)
            return edited_scene.clip

    def _process_scene_effects(self, scene: Scene):
        self._currenty_applied_effects = []
        while self._continue_add_effects():
            usable_effects = self._usable_effects(scene.length())
            if usable_effects == []:
                break
            next_effect = self._select_effect(effects=usable_effects, scene=scene)
            scene.clip = self._apply_effect(scene, next_effect)
            self._currenty_applied_effects.append(next_effect)

    def _apply_effect(self, scene: Scene, effect: Effect) -> VideoClip:
        scene_length = scene.length()
        scene_length = self.get_effect_length(effect, scene_length)
        scene.clip = scene.clip.subclip(0, scene_length)
        print(f"INFO: Applied {effect.__class__.__name__}")
        transformed_clip = effect.apply(
            scene=scene, strength=self._choose_effect_strength()
        )
        if transformed_clip is None:
            raise ValueError
        self.intensity += scene_length * effect.intensity
        return transformed_clip

    def _choose_effect_strength(self):
        return random.random()

    def can_apply(self, effect: Effect, scene_length: float):
        total_intensity = scene_length * effect.intensity
        if total_intensity + self.intensity > self.max_intensity:
            if (
                effect.can_cut
                and effect.min_len * effect.intensity + self.intensity
                <= self.max_intensity
            ):
                return True
            else:
                return False
        return True

    def _usable_effects(self, scene_length: float):
        if self._previous_effect() is None:
            return [e for e in self.effects if self.can_apply(e, scene_length)]
        else:
            return [
                e
                for e in self.effects
                if type(e) in self._previous_effect().compatible_effects()
            ]

    def _select_effect(self, effects: List[Effect], scene: Scene):
        selection_scores = np.array([e.selection_score(scene) for e in effects])
        if self._previous_effect() is not None:
            neighbor_scores = np.array(
                [self._previous_effect().neighbor_score(e) for e in effects]
            )
        else:
            neighbor_scores = np.ones(len(selection_scores))
        config_weights = np.ones(len(selection_scores))
        effect_scores = (
            SELECTION_SCORE_WEIGHT * selection_scores
            + NEIGHBOR_SCORE_WEIGHT * neighbor_scores
        ) * config_weights
        # Normalize
        effect_scores /= sum(effect_scores)
        sample = np.random.multinomial(1, effect_scores, size=1)
        chosen_effect_index = np.where(sample[0] == 1)[0].item()
        return effects[chosen_effect_index]

    def get_effect_length(self, effect: Effect, scene_length: float):
        if effect.can_cut:
            if effect.min_len * effect.intensity + self.intensity > self.max_intensity:
                raise Exception(
                    "Chosen effect's intensity to too high with minimum cut length"
                )
            return effect.effect_length(scene_length)
        else:
            if effect.intensity * scene_length + self.intensity > self.max_intensity:
                raise Exception(
                    "Chosen effect's intensity to too high without allowing cut"
                )
            return scene_length
