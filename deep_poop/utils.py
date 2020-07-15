import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import concatenate_videoclips


def combine_video_clips(video_clips):
    video_clip = concatenate_videoclips(video_clips)
    video_clip.audio = combine_audio_clips(
        [c.audio for c in video_clips], video_clips[0].audio.fps,
    )
    [c.close() for c in video_clips]
    return video_clip


def combine_audio_clips(audio_clips, fps):
    clips_frames = [c.to_soundarray() for c in audio_clips]
    audio_frames = np.concatenate(clips_frames)
    return AudioArrayClip(audio_frames, fps)
