from typing import List

import scenedetect

from deep_poop.scene import Scene


class SceneCutter:
    """Helper class for cutting scenes and sub-scenes

    Args:
        scene_threshold (float): Threshold at which to cut video into clips
        subscene_threshold (float): Threshold to cut clips into sub-clips
        scene_min (int): Minimum length of scene in frames
        subscene_min (int): Minimum length of subscene in frames
        downscale (float, optional): Downscale factor when performing scene detection. If None detect value automatically (Defaults to None)
    """

    def __init__(
        self,
        scene_threshold: float,
        subscene_threshold: float,
        scene_min_len: int,
        subscene_min_len: int,
        downscale: float = None,
    ):
        self.scene_threshold = scene_threshold
        self.subscene_threshold = subscene_threshold
        self.scene_min_len = scene_min_len
        self.subscene_min_len = subscene_min_len
        self.downscale = downscale

    @property
    def subscene_threshold(self):
        if not hasattr(self, "_subscene_threshold"):
            return None
        return self._subscene_threshold

    @property
    def scene_threshold(self):
        if not hasattr(self, "_scene_threshold"):
            return None
        return self._scene_threshold

    @subscene_threshold.setter
    def subscene_threshold(self, val):
        if val < 0 or val > 100:
            raise ValueError("Subscene detection threshold must be within range 0-100")
        if self.scene_threshold is not None and val >= self.scene_threshold:
            raise ValueError(
                "Subscene detection threhold greater or equal to scene threshold"
            )
        self._subscene_threshold = val

    @scene_threshold.setter
    def scene_threshold(self, val):
        if val < 0 or val > 100:
            raise ValueError("Scene detection threshold must be within range 0-100")
        if self.subscene_threshold is not None and val <= self.subscene_threshold:
            raise ValueError(
                "Scene detection threhold smaller or equal to subscene threshold"
            )
        self._scene_threshold = val

    def get_scenes(self, video_file):
        return self.split_scenes(
            video_file=video_file,
            threshold=self.scene_threshold,
            min_len=self.scene_min_len,
        )

    def find_subscenes(self, scene: Scene):
        return self.split_scenes(
            video_file=scene.video_file,
            threshold=self.subscene_threshold,
            min_len=self.subscene_min_len,
            start=scene.start,
            end=scene.end,
        )

    def split_scenes(
        self,
        video_file: str,
        threshold: float,
        min_len: int,
        start: int = None,
        end: int = None,
    ) -> List[Scene]:
        """Splits a video clip into scenes.

        Args:
            video_file (str): Path to video file
            threshold: (float): Non-similarity threshold at which to split scenes (0-100)
            min_len (int): Minimum length of scenes in frames
            start (int, optional): Frame to start splitting from (Defaults to None)
            end (int, optional): Frame until to split (Defaults to None)

        Returns:
            List[Scene]: List of split Scenes
        """
        scenes = []
        try:
            video_manager = scenedetect.VideoManager([video_file])
            scene_manager = scenedetect.SceneManager()
            scene_manager.add_detector(scenedetect.ContentDetector(threshold, min_len))
            video_manager.set_downscale_factor(self.downscale)
            base_timecode = video_manager.get_base_timecode()
            if start is not None and end is not None:
                video_manager.set_duration(
                    start_time=base_timecode + start, end_time=base_timecode + end
                )
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)
            scene_list = scene_manager.get_scene_list(base_timecode)
            for s in scene_list:
                scenes.append(
                    Scene(
                        video_file=video_file, start=s[0].frame_num, end=s[1].frame_num
                    )
                )
        finally:
            video_manager.release()
        return scenes