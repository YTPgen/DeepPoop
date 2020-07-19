from typing import List
import random
import copy
import numpy as np
import math

from moviepy.editor import VideoClip

from deep_poop.utils import combine_video_clips
from deep_poop.scene import Scene
from deep_poop.effects.effect import Effect
from deep_poop.config import SELECTION_SCORE_WEIGHT, NEIGHBOR_SCORE_WEIGHT

# TODO: Move to conf
A = -1 / 70
B = -1 / 25


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
        self._effects_to_apply = []
        self._next_effect_intensity_threshold = (
            max(1 - easy_start, 0) * self.max_intensity
        )

    def _set_next_effect_trigger_threshold(self):
        self._next_effect_intensity_threshold = random.random() * self.max_intensity

    def _time_until_next_effect(self):
        current_point = self._intensity_to_time(self.intensity)
        target_point = self._intensity_to_time(self._next_effect_intensity_threshold)
        return target_point - current_point

    def _previous_effect(self):
        if len(self._effects_to_apply) == 0:
            return None
        return self._effects_to_apply[-1]

    def _continue_add_effects(self):
        if (
            self._previous_effect() is not None
            and not self._previous_effect().standalone
            and len(self._effects_to_apply) == 1
        ):
            return True
        return self.intensity < self.max_intensity

    def _add_intensity(self, amount: float):
        self.intensity = min(self.intensity + amount, self.max_intensity)

    def _time_to_intensity(self, time: float) -> float:
        return (1 + (time ** 2) * A + time * B) * self.max_intensity

    def _intensity_to_time(self, intensity: float) -> float:
        intensity = min(intensity, self.max_intensity)
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
        return self.intensity - self._time_to_intensity(x2)

    def feed_scene(self, scene: Scene) -> VideoClip:
        _time_until_next_effect = self._time_until_next_effect()
        if (
            _time_until_next_effect > 0
            and _time_until_next_effect > scene.length() - self.min_effect_length
        ):
            print(f"INFO: No effect applied")
            intensity_loss = self._intensity_loss(scene.length())
            print(f"INFO: Intensity reduced by {intensity_loss}")
            self.intensity -= intensity_loss
            edited_clip = scene.clip
        else:
            self._set_next_effect_trigger_threshold()
            if _time_until_next_effect > 0:
                scene_before = scene.subscene(start=0, end=_time_until_next_effect)
                edited_scene = scene.subscene(
                    start=_time_until_next_effect, end=scene.length(),
                )
                self._process_scene_effects(edited_scene)
                edited_clip = combine_video_clips(
                    [scene_before.clip, edited_scene.clip]
                )
            else:
                edited_scene = scene.subscene(start=0, end=scene.length())
                self._process_scene_effects(edited_scene)
                edited_clip = edited_scene.clip
            print(f"INFO: Current intensity {self.intensity}/{self.max_intensity}")
        return edited_clip

    def _process_scene_effects(self, scene: Scene):
        self._select_effects(scene)
        while len(self._effects_to_apply) > 0:
            next_effect = self._effects_to_apply.pop()
            self._apply_effect(scene, next_effect)

    def _select_effects(self, scene: Scene):
        self._effects_to_apply = []
        while self._continue_add_effects():
            usable_effects = self._usable_effects(scene.length())
            if usable_effects == []:
                return
            next_effect = self._select_effect(effects=usable_effects, scene=scene)
            self._effects_to_apply.append(next_effect)

    def _apply_effect(self, scene: Scene, effect: Effect) -> VideoClip:
        scene_length = scene.length()
        effect_length = max(effect.effect_length(scene_length), 1 / scene.clip.fps)
        if effect_length >= scene_length:
            transformed_clip = scene.clip = effect.apply(
                scene=scene, strength=self._choose_effect_strength()
            )
        else:
            effect_begin = random.uniform(0, scene_length - effect_length)
            scene_before = scene.subscene(0, effect_begin)
            scene_after = scene.subscene(effect_begin + effect_length, scene_length)
            effect_scene = scene.subscene(
                start=effect_begin, end=effect_begin + effect_length
            )
            transformed_clip = effect.apply(
                scene=effect_scene, strength=self._choose_effect_strength()
            )
            scene.clip = combine_video_clips(
                [scene_before.clip, transformed_clip, scene_after.clip]
            )
        if scene.clip is None:
            raise ValueError
        print(f"INFO: Applied {effect.name}")
        intensity_cost = effect_length * effect.intensity
        self._add_intensity(intensity_cost)
        print(f"INFO: Added {intensity_cost} intensity")
        return transformed_clip

    def _choose_effect_strength(self):
        return random.random()

    def can_apply(self, effect: Effect, scene_length: float):
        if effect in self._effects_to_apply:
            return False
        if not effect.can_cut and scene_length < effect.min_len:
            return False
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
            usable_effects = [
                e for e in self.effects if self.can_apply(e, scene_length)
            ]
        else:
            usable_effects = [
                e
                for e in self.effects
                if e.name in self._previous_effect().compatible_effects()
                and self.can_apply(e, scene_length)
            ]
        return usable_effects

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
