import pytest

from deep_poop.effect_applier import EffectApplier
from deep_poop.clips.cut_clip import CutClip
from test.utils import scene_frames_identical


@pytest.fixture(scope="session")
def effect_applier():
    return EffectApplier(20, 0)


def test_effect_applier_skip(effect_applier, scene):
    effect_applier.max_intensity = 20
    effect_applier.intensity = 30
    frames_before = CutClip(scene.clip).frames
    changed_clip = effect_applier.feed_scene(scene)
    frames_after = CutClip(scene.clip).frames
    assert scene_frames_identical(
        frames_before, frames_after
    ), "Scene object clip is different after effect applier. Should only return altered copy."


def test_effect_applier_applied(effect_applier, scene):
    frames_before = CutClip(scene.clip).frames
    changed_clip = effect_applier.feed_scene(scene)
    frames_after = CutClip(scene.clip).frames
    assert scene_frames_identical(
        frames_before, frames_after
    ), "Scene object clip is different after effect applier. Should only return altered copy."
    assert not scene_frames_identical(
        frames_before, CutClip(changed_clip).frames
    ), "Scene after effect is identical to before effect applier"

