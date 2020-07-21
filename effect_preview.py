from fire import Fire
from moviepy.editor import VideoFileClip

import deep_poop.effects
from deep_poop.scene import Scene

test_scene_file = "test/clips/sup_bro.mp4"
clip_length = 8


def get_test_scene():
    clip = VideoFileClip(test_scene_file).subclip(0, clip_length)
    test_scene = Scene(clip)
    test_scene.analyze_frames()
    return test_scene


def preview_effect(effect: str, strength: float = 1.0, **kwargs):
    kwargs["intensity"] = 1
    effect_class = getattr(deep_poop.effects, effect)
    effect = effect_class(**kwargs)
    test_scene = get_test_scene()
    transformed_clip = effect.apply(test_scene, strength)
    transformed_clip.preview()


if __name__ == "__main__":
    Fire(preview_effect)
