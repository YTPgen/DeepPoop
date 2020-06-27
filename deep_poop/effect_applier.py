from typing import List
import random

from moviepy.editor import VideoClip

from deep_poop.scene import Scene
from deep_poop.effects import effects, Effect


class EffectApplier:
    def __init__(self, max_intensity: float, easy_start: float = 0):
        self.intensity = easy_start
        self.max_intensity = max_intensity

    def skip_effect(self):
        return random.random() < self.intensity / self.max_intensity

    def apply_effects(self, video: VideoClip, scene: Scene):
        scene_length = scene.length() / video.fps
        if not self.skip_effect():
            usable_effects = self.usable_effects(scene_length)
            # TODO: Change to use multiple effects at same time
            if usable_effects != []:
                effect = self.select_effect(usable_effects)
                scene_length = self.get_effect_length(effect, scene_length)
                video = video.subclip(0, scene_length)
                self.intensity += scene_length * effect.intensity
                self.intensity -= scene_length
                print(f"INFO: Applied {effect.name}")
                return effect.apply(video)
        else:
            print(f"DEBBUG: Skipped applying effect")
            self.intensity -= scene_length
            return video

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
        return [e for e in effects if self.can_apply(e, scene_length)]

    def select_effect(self, effects: List[Effect]):
        return random.choice(effects)

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
