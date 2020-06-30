import random
from fire import Fire
from moviepy.editor import VideoFileClip, concatenate_videoclips
from deep_poop.scene_cutter import SceneCutter
from deep_poop.effect_applier import EffectApplier


class Generator:
    """Generator for YTP videos

    Args:
        video_file (str): Video file for source material
        scene_threshold (float): Threshold at which to cut video into clips
        subscene_threshold (float): Threshold to cut clips into sub-clips
        scene_min_len (int): Minimum length of scene in frames (Defaults to 600)
        subscene_min_len (int): Minimum length of subscene in frames (Defaults to 120)
        length (float): Lengths of desired video in seconds. If 'reuse' is set to False total length might shorter
        abruptness (float, optional): Probability to transition to new scene after sub-scene end (Defaults to 0.2)
        reuse (bool, optional): Toggles whether to re-use same scenes (Defaults to True)
        downscale (float, optional): Downscale factor when performing scene detection. If None detect value automatically (Defaults to None)
    """

    def __init__(
        self,
        video_file: str,
        scene_threshold: float,
        subscene_threshold: float,
        length: float,
        scene_min_len: int = 600,
        subscene_min_len: int = 120,
        abruptness: float = 0.2,
        reuse: bool = True,
        downscale: float = None,
        max_intensity=20,
        easy_start=0,
    ):
        self.video_file = video_file
        self._scene_cutter = SceneCutter(
            scene_threshold=scene_threshold,
            subscene_threshold=subscene_threshold,
            scene_min_len=scene_min_len,
            subscene_min_len=subscene_min_len,
            downscale=downscale,
        )
        self.length = length
        self._effect_applier = EffectApplier(
            max_intensity=max_intensity, easy_start=easy_start
        )
        self.reuse = reuse
        self.abruptness = abruptness

    def generate(self):
        video = VideoFileClip(self.video_file)
        scenes = self._scene_cutter.get_scenes(self.video_file)
        for s in scenes:
            s.subscenes = self._scene_cutter.find_subscenes(s)
        total_duration = 0
        ytp_clips = []
        while len(scenes) > 0 and total_duration < self.length:
            next_i = random.randint(0, len(scenes) - 1) if len(scenes) > 1 else 0
            current_scene = scenes[next_i] if self.reuse else scenes.pop(next_i)
            # TODO: Make so can start in middle
            from_subscene = 0
            until_subscene = from_subscene + 1
            for i in range(from_subscene, len(current_scene.subscenes) - 1):
                if random.random() < self.abruptness:
                    break
                until_subscene += 1

            subscenes = current_scene.subscenes[from_subscene:until_subscene]
            for s in subscenes:
                subscene_clip = video.subclip(s.start / video.fps, s.end / video.fps)
                print(f"Applying effect at {total_duration}")
                new_clip = self._effect_applier.apply_effects(subscene_clip, s)
                ytp_clips.append(new_clip)
                total_duration += new_clip.duration
        output_video = concatenate_videoclips(ytp_clips)
        output_video.write_videofile("test.mp4")