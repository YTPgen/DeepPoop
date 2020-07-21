import os
import tempfile

import librosa
from moviepy.audio.io.AudioFileClip import AudioFileClip

import deep_poop.effects.effect as effect
from deep_poop.scene import Scene


class Pitch(effect.Effect):
    """Shifts an audio clip by a given amount of semitone steps.

    Args:
        min_steps (int): Amount of steps to shift
        max_steps (int): Amount of steps to shift

    """

    def __init__(self, min_steps: int, max_steps: int, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.AUDIO
        super(Pitch, self).__init__(*args, **kwargs)
        self.min_steps = min_steps
        self.max_steps = max_steps

    def initialize_effect(self, strength: float):
        self.steps = self.min_steps + int((self.max_steps - self.min_steps) * strength)

    def effect_function(self, scene: Scene):
        video = scene.clip
        audio = video.audio
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_file = os.path.join(tmpdir, "tmp.wav")
            pitched_file = os.path.join(tmpdir, "pitched.wav")
            audio.write_audiofile(tmp_file, logger=None)
            y, sr = librosa.core.load(tmp_file, audio.fps)
            y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=self.steps)
            librosa.output.write_wav(pitched_file, y_shifted, sr)
            video.audio = AudioFileClip(pitched_file)
            return video
