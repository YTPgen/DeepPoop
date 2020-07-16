import math

from moviepy.editor import VideoClip

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils
from deep_poop.scene import Scene


class Robotify(effect.Effect):
    """Modifies audio track by multiplying it with a sine wave.

    Args:
        min_freq (float): Minimum frequency of sine wave
        max_freq (float): Maximum frequency of sine wave

    """

    def __init__(self, min_freq: float, max_freq: float, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.AUDIO
        super(Robotify, self).__init__(*args, **kwargs)
        self.min_freq = min_freq
        self.max_freq = max_freq

    def initialize_effect(self, strength: float):
        self.angle = 0
        self.frequency = (self.max_freq - self.min_freq) * strength + self.min_freq

    def effect_function(self, scene: Scene):
        video = scene.clip
        audio = video.audio
        audio_frames = utils.audio_to_frames(audio)
        for t in range(len(audio_frames)):
            audio_frames[t] *= math.sin(t / self.frequency)
        video.audio = utils.frames_to_audio(audio_frames, video.audio.fps)
        return video
