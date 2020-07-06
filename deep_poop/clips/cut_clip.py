import moviepy.editor
import numpy as np

from moviepy.audio.AudioClip import AudioArrayClip


class FullFrame(object):
    """Helper class for storing a video frame
    and its respective audio frames.

    Args:
        video_frame: Video frame of frame
        audio_frames: Audio frames of frame
    """

    def __init__(self, video_frame, audio_frames):
        self.video_frame = video_frame
        self.audio_frames = audio_frames
        self.face_locations = []

    def __eq__(self, other):
        if not isinstance(other, FullFrame):
            return False
        if not np.ndarray.all(self.video_frame == other.video_frame):
            return False
        if not np.ndarray.all(self.audio_frames == other.audio_frames):
            return False
        return True


class CutClip(object):
    """Helper class for cutting a video into video
    frames and their respective audio.
    
    Args:
            video_clip (moviepy.editor.VideoFileClip): Video clip to cut from
    """

    def __init__(self, video_clip: moviepy.editor.VideoClip):
        self.video_fps = video_clip.fps
        self.audio_fps = video_clip.audio.fps
        self.frames = self.video_to_frames(video_clip)

    def video_to_frames(self, video_clip: moviepy.editor.VideoClip):
        """Cuts a video into a sequence of FullFrame objects.

        Args:
            video_clip (moviepy.editor.VideoFileClip): Video to cut

        Returns:
            [type]: Video as list of FullFrame
        """
        audio_frames = video_clip.audio.to_soundarray()
        frames = []
        i = 0
        audio_frames_per_frame = video_clip.audio.fps / video_clip.fps
        for t, video_frame in video_clip.iter_frames(with_times=True):
            copy_from = i
            i = i + audio_frames_per_frame
            next_frame = FullFrame(video_frame, audio_frames[int(copy_from) : int(i)])
            frames.append(next_frame)
        return frames

    def to_video(self) -> moviepy.editor.VideoClip:
        """Recreates video clip from self-contained list
        of full frames.

        Returns:
            moviepy.editor.VideoFileClip: Reconstructed video clip
        """
        video_frames = [f.video_frame for f in self.frames]
        afs = [af.audio_frames for af in self.frames]
        audio_frames = np.array([item for sublist in afs for item in sublist])
        video = moviepy.editor.ImageSequenceClip(video_frames, self.video_fps)
        video.audio = AudioArrayClip(audio_frames, self.audio_fps)
        return video
