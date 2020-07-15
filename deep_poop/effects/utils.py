import numpy as np
import functools
from moviepy.audio.AudioClip import AudioArrayClip, AudioClip


def audio_to_frames(audio: AudioClip):
    return audio.to_soundarray()


def frames_to_audio(frames: np.ndarray, fps: float):
    return AudioArrayClip(frames, fps)

