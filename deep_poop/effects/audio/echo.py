from moviepy.editor import VideoClip

import deep_poop.effects.effect as effect
import deep_poop.effects.utils as utils
from deep_poop.scene import Scene


class Echo(effect.Effect):
    """Puts an echo in the audio track with given delay and strength.

    Args:
        delay (float): Delay of echo in seconds
        strength (float): Strength of echo relative to original sound

    """

    def __init__(self, delay: float, strength: float = 0.7, *args, **kwargs):
        kwargs["effect_type"] = effect.EffectType.AUDIO
        super(Echo, self).__init__(*args, **kwargs)
        self.delay = delay
        self.strength = strength

    def effect_function(self, scene: Scene, workers: int):
        video = scene.clip
        audio = video.audio
        audio_frames = utils.audio_to_frames(audio)
        d = int(audio.fps * self.delay)
        for i in range(len(audio_frames) - d):
            audio_frames[i] += audio_frames[i - d] * self.strength
        video.audio = utils.frames_to_audio(audio_frames, video.audio.fps)
        return video
