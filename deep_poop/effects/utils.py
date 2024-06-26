import numpy as np
from deep_poop.scene import Scene
from moviepy.audio.AudioClip import AudioArrayClip, AudioClip


def audio_to_frames(audio: AudioClip):
    return audio.to_soundarray()


def frames_to_audio(frames: np.ndarray, fps: float):
    return AudioArrayClip(frames, fps)
