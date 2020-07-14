import numpy as np
import functools
from moviepy.audio.AudioClip import AudioArrayClip, AudioClip


def audio_to_frames(audio: AudioClip):
    return audio.to_soundarray()


def frames_to_audio(frames: np.ndarray, fps: float):
    return AudioArrayClip(frames, fps)


def combine_audio_clips(audio_clips, fps):
    clips_frames = [audio_to_frames(c) for c in audio_clips]
    audio_frames = np.concatenate(clips_frames)
    return frames_to_audio(audio_frames, fps)

