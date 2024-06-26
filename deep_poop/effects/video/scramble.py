import random

from moviepy.editor import VideoClip

from deep_poop.clips.cut_clip import CutClip
from deep_poop.scene import Scene
import deep_poop.effects.effect as effect


class Scramble(effect.Effect):
    """Scrambles the order of frames in a clip.

    Args:
        min_scramble_frame_length (int, optional): Minimum length of each scramble sequence. Defaults to 1.
        max_scramble_frame_length (int, optional): Maximum length of each scramble sequence. Defaults to 1.
        unique_scramble (bool, optional): If set to True allow to reuse same frames. Defaults to True.

    """

    def __init__(
        self,
        min_scramble_frame_length=1,
        max_scramble_frame_length=1,
        unique_scramble=True,
        *args,
        **kwargs
    ):
        kwargs["effect_type"] = effect.EffectType.VIDEO
        super(Scramble, self).__init__(*args, **kwargs)
        self.unique_scramble = unique_scramble
        self.min_scramble_frame_length = min_scramble_frame_length
        self.max_scramble_frame_length = max_scramble_frame_length

    def initialize_effect(self, scene: Scene, strength: float):
        self.scramble_frame_length = int(
            (self.max_scramble_frame_length - self.min_scramble_frame_length) * strength
            + self.min_scramble_frame_length
        )

    def effect_function(self, scene: Scene, workers: int):
        cut_clip = CutClip(scene.clip)

        scrambled_frames = []
        clip_frames_length = len(cut_clip.frames)
        while (
            len(cut_clip.frames) >= self.scramble_frame_length
            and len(scrambled_frames) < clip_frames_length
        ):
            max_start_index = len(cut_clip.frames) - self.scramble_frame_length
            frame_index = (
                0 if max_start_index == 0 else random.randint(0, max_start_index)
            )
            for f in cut_clip.frames[
                frame_index : frame_index + self.scramble_frame_length
            ]:
                scrambled_frames.append(f)
            if self.unique_scramble:
                del cut_clip.frames[
                    frame_index : frame_index + self.scramble_frame_length
                ]
        if self.unique_scramble:
            for f in cut_clip.frames:
                scrambled_frames.append(f)
        if len(scrambled_frames) > clip_frames_length:
            scrambled_frames = scrambled_frames[:clip_frames_length]
        cut_clip.frames = scrambled_frames
        return cut_clip.to_video()
