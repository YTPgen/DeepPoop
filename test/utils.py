from typing import List

from deep_poop.clips.cut_clip import FullFrame


def scene_frames_identical(a: List[FullFrame], b: List[FullFrame]):
    for f_a, f_b in zip(a, b):
        if not f_a == f_b:
            return False
    return True

