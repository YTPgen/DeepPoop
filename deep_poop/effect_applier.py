import copy
import math
import random
from typing import List

import numpy as np
from moviepy.editor import VideoClip
from numpy.lib.function_base import select

from deep_poop.config import NEIGHBOR_SCORE_WEIGHT, SELECTION_SCORE_WEIGHT
from deep_poop.effects.effect import Effect, EffectType
from deep_poop.effects.effect_graph import EffectGraph, EffectNode
from deep_poop.scene import Scene
from deep_poop.utils import combine_video_clips

# TODO: Move to conf
A = -1 / 70
B = -1 / 25


class EffectApplier:
    def __init__(
        self,
        max_intensity: float,
        effect_graph: EffectGraph,
        easy_start: float = 0,
        min_effect_length: float = 1.0,
        max_simultaneous_effects=3,
    ):
        self.intensity = easy_start
        self.max_intensity = max_intensity
        self.effect_graph = effect_graph
        self.min_effect_length = min_effect_length
        self._effects_to_apply = []
        self._next_effect_intensity_threshold = (
            max(1 - easy_start, 0) * self.max_intensity
        )
        self.last_effect_length = 0
        self.max_simultaneous_effects = max_simultaneous_effects

    def _set_next_effect_trigger_threshold(self):
        self._next_effect_intensity_threshold = random.random() * self.intensity

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
        if len(self._effects_to_apply) >= self.max_simultaneous_effects:
            return False
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
        _time_until_next_effect = max(self._time_until_next_effect(), 0)
        current_point_in_scene = 0
        edited_scene = scene.subscene(0, scene.clip.duration)
        times_edited = 0
        while (
            _time_until_next_effect + current_point_in_scene
            <= scene.length() - self.min_effect_length
        ):
            self._set_next_effect_trigger_threshold()
            current_point_in_scene += _time_until_next_effect
            print(
                f"DEBUG: Applying effects at point {current_point_in_scene}s in scene"
            )
            if _time_until_next_effect > 0:
                scene_before = edited_scene.subscene(
                    start=0,
                    end=current_point_in_scene,
                )
                effect_scene = edited_scene.subscene(
                    start=current_point_in_scene,
                    end=scene.length(),
                )
                self._process_scene_effects(effect_scene)
                edited_scene.clip = combine_video_clips(
                    [scene_before.clip, effect_scene.clip]
                )
            else:
                self._process_scene_effects(edited_scene)
            print(f"INFO: Current intensity {self.intensity}/{self.max_intensity}")
            current_point_in_scene += self.last_effect_length
            _time_until_next_effect = self._time_until_next_effect()
            times_edited += 1
        if times_edited == 0:
            print(f"INFO: No effect applied")
        intensity_loss = self._intensity_loss(scene.length() - current_point_in_scene)
        print(f"INFO: Intensity reduced by {intensity_loss}")
        self.intensity -= intensity_loss
        return edited_scene.clip

    def _process_scene_effects(self, scene: Scene):
        self._select_effects(scene)
        if self._effects_to_apply == []:
            print("INFO: No effects could be applied to scene")
            return
        effect_lengths = [
            max(effect.effect_length(scene.length()), 1 / scene.clip.fps)
            for effect in self._effects_to_apply
        ]
        longest_effect_duration = max(effect_lengths)
        effect_scene = scene.subscene(0, longest_effect_duration)
        scene_after = scene.subscene(longest_effect_duration, scene.length())
        while len(self._effects_to_apply) > 0:
            next_effect = self._effects_to_apply.pop()
            duration = effect_lengths.pop()
            self._apply_effect(effect_scene, next_effect, duration)
            intensity_cost = duration * next_effect.intensity
            self._add_intensity(intensity_cost)
            # print(f"DEBUG: Added {intensity_cost} intensity")
        scene.clip = combine_video_clips([effect_scene.clip, scene_after.clip])
        self.last_effect_length = longest_effect_duration

    def _select_effects(self, scene: Scene):
        self._effects_to_apply = []
        while self._continue_add_effects():
            previous_effect = self._previous_effect()
            if previous_effect == None:
                next_effect = self._select_initial_effect(scene)
            else:
                next_effect = self._select_next_effect(previous_effect, scene)

            if next_effect == None:
                return
            self._effects_to_apply.append(next_effect)

    def _apply_effect(self, scene: Scene, effect: Effect, duration: float) -> VideoClip:
        scene_length = scene.length()
        if duration >= scene_length:
            transformed_clip = scene.clip = effect.apply(
                scene=scene, strength=self._choose_effect_strength()
            )
        else:
            effect_begin = random.uniform(0, scene_length - duration)
            scene_before = scene.subscene(0, effect_begin)
            scene_after = scene.subscene(effect_begin + duration, scene_length)
            effect_scene = scene.subscene(
                start=effect_begin, end=effect_begin + duration
            )
            transformed_clip = effect.apply(
                scene=effect_scene, strength=self._choose_effect_strength()
            )
            scene.clip = combine_video_clips(
                [scene_before.clip, transformed_clip, scene_after.clip]
            )
        if scene.clip is None:
            raise ValueError
        print(f"INFO: Applied {effect.name} with length {duration}s")
        return transformed_clip

    def _choose_effect_strength(self):
        return random.random()

    def _has_audio_effect(self, effects: List[Effect]):
        for e in effects:
            if e.type == EffectType.AUDIO:
                return True
        return False

    def can_apply(self, effect: Effect, scene_length: float):
        if effect in self._effects_to_apply:
            return False
        if effect.type == EffectType.AUDIO and self._has_audio_effect(
            self._effects_to_apply
        ):
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

    def _select_initial_effect(self, scene: Scene) -> Effect:
        usable_effects = [
            e for e in self.effect_graph.effects if self.can_apply(e, scene.length())
        ]
        if len(usable_effects) == 0:
            return None
        effect_scores = np.array([e.selection_score(scene) for e in usable_effects])
        return self._pick_random_weighted(usable_effects, effect_scores)

    def _select_next_effect(self, previous_effect: Effect, scene: Scene):
        connections: EffectNode.EffectConnection = [
            c
            for c in self.effect_graph.get_effect_connections(previous_effect)
            if self.can_apply(c.other.effect, scene.length())
        ]
        if len(connections) == 0:
            return None
        selection_scores = np.array(
            [c.other.effect.selection_score(scene) for c in connections]
        )
        neighbor_scores = np.array([c.weight for c in connections])
        effect_scores = (
            SELECTION_SCORE_WEIGHT * selection_scores
            + NEIGHBOR_SCORE_WEIGHT * neighbor_scores
        )
        return self._pick_random_weighted(
            [c.other.effect for c in connections], effect_scores
        )

    def _pick_random_weighted(self, elements: List, weights: np.array):
        if len(elements) != len(weights):
            return ValueError(
                f"Elements amount {len(elements)} and weights amount {len(weights)} does not match"
            )
        weights /= sum(weights)
        sample = np.random.multinomial(1, weights, size=1)
        chosen_effect_index = np.where(sample[0] == 1)[0].item()
        return elements[chosen_effect_index]
