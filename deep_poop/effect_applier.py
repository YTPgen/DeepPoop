from typing import List
import random
import copy
import numpy as np

from moviepy.editor import VideoClip

from deep_poop.scene import Scene
from deep_poop.effects.effect import Effect
from deep_poop.config import SELECTION_SCORE_WEIGHT, NEIGHBOR_SCORE_WEIGHT


class EffectApplier:
    def __init__(
        self, max_intensity: float, effects: List[Effect], easy_start: float = 0
    ):
        self.intensity = easy_start
        self.max_intensity = max_intensity
        self.effects = effects

    def skip_effect(self):
        return random.random() < self.intensity / self.max_intensity

    def feed_scene(self, scene: Scene):
        scene_length = scene.length()
        previous_effect = None
        if not self.skip_effect():
            usable_effects = self.usable_effects(scene_length)
            # TODO: Change to use multiple effects at same time
            if usable_effects != []:
                effect = self.select_effect(
                    effects=usable_effects, scene=scene, previous_effect=previous_effect
                )
                original_clip = scene.clip
                scene_length = self.get_effect_length(effect, scene_length)
                scene.clip = scene.clip.subclip(0, scene_length)
                print(f"INFO: Applied {effect.__class__.__name__}")
                transformed_clip = effect.apply(scene)
                scene.clip = original_clip
                self.intensity += scene_length * effect.intensity
                self.intensity -= scene_length
                if transformed_clip is None:
                    raise ValueError
                return transformed_clip
        print(f"DEBUG: Skipped applying effect")
        self.intensity -= scene_length
        return scene.clip

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

    def usable_effects(self, scene_length: float):
        return [e for e in self.effects if self.can_apply(e, scene_length)]

    def select_effect(
        self, effects: List[Effect], scene: Scene, previous_effect: Effect
    ):
        selection_scores = np.array([e.selection_score(scene) for e in effects])
        if previous_effect is not None:
            neighbor_scores = np.array(
                [previous_effect.neighbor_score(e) for e in effects]
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
