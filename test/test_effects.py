from typing import List
import pytest
from deep_poop.scene import Scene
from deep_poop.clips.cut_clip import CutClip, FullFrame
from deep_poop.effects.effect import EffectLengthDistribution


def assert_effect_length(effect):
    min_l, max_l = 2, 10
    effect.max_len = max_l
    effect.min_len = min_l
    effect_length = effect.effect_length(20)
    assert effect_length >= min_l
    assert effect_length <= max_l


class EffectTest:
    def __init__(self, effect, scene):
        self.effect = effect
        self.run_test(scene)

    def run_test(self, scene):
        self.test_get_length()
        self.test_apply(scene)
        self.test_selection_score(scene)

    def test_get_length(self):
        assert_effect_length(self.effect)

    def test_apply(self, scene):
        frames_before = CutClip(scene.clip).frames
        changed_clip = self.effect.apply(scene)
        frames_after = CutClip(scene.clip).frames
        # Check that effect did not change the scene object itself
        assert self.scene_frames_identical(
            frames_before, frames_after
        ), "Scene frames are different after effect"
        assert not self.scene_frames_identical(
            frames_before, CutClip(changed_clip).frames
        ), "Scene after effect is identical to before"

    def test_selection_score(self, scene):
        score = self.effect.selection_score(scene)
        assert isinstance(score, float)

    def scene_frames_identical(self, a: List[FullFrame], b: List[FullFrame]):
        for f_a, f_b in zip(a, b):
            if not f_a == f_b:
                return False
        return True


def test_effect_not_implemented(scene, test_effect):
    with pytest.raises(NotImplementedError):
        test_effect.apply(scene)


def test_random_length(test_effect):
    test_effect.length_distribution = EffectLengthDistribution.RANDOM
    assert_effect_length(test_effect)


def test_normal_length(test_effect):
    test_effect.length_distribution = EffectLengthDistribution.NORMAL
    assert_effect_length(test_effect)


def test_echo(scene, echo):
    effect_test = EffectTest(echo, scene)


def test_pixelate(scene, pixelate):
    effect_test = EffectTest(pixelate, scene)


def test_invert(scene, invert):
    effect_test = EffectTest(invert, scene)


def test_rotate(scene, rotate):
    effect_test = EffectTest(rotate, scene)


def test_scramble_nonunique(scene, scramble):
    scramble.unique = False
    effect_test = EffectTest(scramble, scene)


def test_scramble_unique(scene, scramble):
    scramble.unique = True
    effect_test = EffectTest(scramble, scene)
