from deep_poop.build_effect_graph import EFFECT_GRAPH
import random
import tempfile
import shutil
import os

from fire import Fire
from moviepy.editor import VideoFileClip, concatenate_videoclips, VideoClip

from deep_poop.scene_cutter import SceneCutter
from deep_poop.effect_applier import EffectApplier
from deep_poop.utils import combine_audio_clips, combine_video_clips
from deep_poop.scene import Scene


class Generator:
    """Generator for YTP videos

    Args:
        video_file (str): Video file for source material
        out_file (str): File name of produced video
        scene_threshold (float): Threshold at which to cut video into clips
        subscene_threshold (float): Threshold to cut clips into sub-clips
        work_dir (str): Working directory for storing files such as analysis caches
        scene_min_len (int): Minimum length of scene in frames (Defaults to 600)
        subscene_min_len (int): Minimum length of subscene in frames (Defaults to 120)
        length (float): Lengths of desired video in seconds. If 'reuse' is set to False total length might shorter
        abruptness (float, optional): Probability to transition to new scene after sub-scene end (Defaults to 0.2)
        reuse (bool, optional): Toggles whether to re-use same scenes (Defaults to True)
        downscale (float, optional): Downscale factor when performing scene detection. If None detect value automatically (Defaults to None)
        workers (int, optional): Amount of workers to process each effect (if effect allows it). A higher number could lead to faster generation (Defaults to 1)
    """

    def __init__(
        self,
        video_file: str,
        out_file: str,
        scene_threshold: float,
        subscene_threshold: float,
        length: float,
        work_dir: str = "./work",
        scene_min_len: int = 600,
        subscene_min_len: int = 90,
        abruptness: float = 0.2,
        reuse: bool = True,
        downscale: float = None,
        max_intensity=20,
        easy_start=0,
        workers=1,
    ):
        self.video_file = video_file
        self.out_file = out_file
        self._scene_cutter = SceneCutter(
            scene_threshold=scene_threshold,
            subscene_threshold=subscene_threshold,
            scene_min_len=scene_min_len,
            subscene_min_len=subscene_min_len,
            downscale=downscale,
            work_dir=os.path.join(work_dir, os.path.basename(video_file)),
        )
        self.length = length
        self._effect_applier = EffectApplier(
            max_intensity=max_intensity,
            easy_start=easy_start,
            effect_graph=EFFECT_GRAPH,
            workers=workers,
        )
        self.reuse = reuse
        self.abruptness = abruptness
        self.work_dir = work_dir

    def ytp_clip_from_scene(self, scene: Scene, abruptness: int):
        scene.analyze_frames()

        subscene = scene.subscene(
            0, scene.length() * (1 - (abruptness * random.random()))
        )
        if subscene.clip is None or subscene.clip.audio is None:
            print(f"Subscene has corrupted clip data. Skipping...")
            return 0
        print(f"DEBUG: Handling subscene with length {subscene.length()}")
        # Fix as scenecutter does not seem to respect minimum length
        if len(subscene.frames) < self._scene_cutter.subscene_min_len:
            print(
                f"WARNING: Skipped subscene as length {len(subscene.frames)} is shorter than minimum"
            )
            return 0
        new_clip = self._effect_applier.feed_scene(subscene)
        print(
            f"DEBUG: Finished applying effects on clip with duration {new_clip.duration}"
        )
        return new_clip

    def _create_and_save_clip(self, scene: Scene, path: str, abruptness: int):
        new_clip = self.ytp_clip_from_scene(scene, abruptness)
        if new_clip == None:
            return 0
        new_clip.write_videofile(path)
        print(f"INFO: Wrote clip of duration {new_clip.duration}s to {path}")
        return new_clip.duration

    def combine(self, dir: str) -> VideoClip:
        """Combines all clips in given directory to one in alphabetical order.

        Args:
            dir (str): Path to directory containing subclips

        Returns:
            VideoClip: Constructed video clip
        """
        clip_files = os.listdir(dir)
        clip_files.sort()
        clips = []
        for c in clip_files:
            clips.append(VideoFileClip(os.path.join(dir, c)))
        return combine_video_clips(clips)

    def generate(self):
        main_video = VideoFileClip(self.video_file)
        scenes = self._scene_cutter.get_scenes(
            video_clip=main_video, video_file=self.video_file
        )
        if not self.reuse:
            self.length = min(self.length, main_video.duration)
        total_duration = 0
        current_clip_index = 1
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                while len(scenes) > 0 and total_duration < self.length:
                    next_i = (
                        random.randint(0, len(scenes) - 1) if len(scenes) > 1 else 0
                    )
                    current_scene = scenes[next_i] if self.reuse else scenes.pop(next_i)
                    duration_left = self.length - total_duration
                    print(f"INFO: Duration left {duration_left}")
                    if current_scene.length() > duration_left:
                        current_scene = current_scene.subscene(0, duration_left)
                        clip_duration = self._create_and_save_clip(
                            current_scene,
                            os.path.join(tmpdir, f"{current_clip_index}.mp4"),
                            0,
                        )
                    else:
                        clip_duration = self._create_and_save_clip(
                            current_scene,
                            os.path.join(tmpdir, f"{current_clip_index}.mp4"),
                            self.abruptness,
                        )
                    if clip_duration > 0:
                        total_duration += clip_duration
                        current_clip_index += 1
                output_video = self.combine(tmpdir)
                output_video = output_video.subclip(0, self.length)
                output_video.write_videofile(self.out_file)
            except Exception as e:
                backup_folder = "backup_clips"
                shutil.rmtree(backup_folder, ignore_errors=True)
                print(
                    f"ERROR: Caught exception {e}. Saving clips produced so far to {backup_folder}..."
                )
                shutil.copytree(tmpdir, backup_folder)
                raise e
