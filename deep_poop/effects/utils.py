import numpy as np
import functools
from moviepy.audio.AudioClip import AudioArrayClip, AudioClip
from moviepy.editor import concatenate_videoclips


def audio_to_frames(audio: AudioClip):
    return audio.to_soundarray()


def frames_to_audio(frames: np.ndarray, fps: float):
    return AudioArrayClip(frames, fps)


def combine_video_clips(video_clips):
    video_clip = concatenate_videoclips(video_clips)
    video_clip.audio = combine_audio_clips(
        [c.audio for c in video_clips], video_clips[0].audio.fps,
    )
    [c.close() for c in video_clips]
    return video_clip


def combine_audio_clips(audio_clips, fps):
    clips_frames = [audio_to_frames(c) for c in audio_clips]
    audio_frames = np.concatenate(clips_frames)
    return frames_to_audio(audio_frames, fps)

