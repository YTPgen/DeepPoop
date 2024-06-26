from deep_poop.effects.effect_graph import EffectGraph
from unittest.mock import MagicMock

import pytest

from deep_poop.effects.effect import Effect
from deep_poop.effect_applier import EffectApplier
from deep_poop.clips.cut_clip import CutClip
from test.utils import scene_frames_identical


@pytest.fixture(scope="session")
def dummy_effect():
    def _apply(scene, strength):
        return scene.clip

    dummy_effect = Effect(intensity=1, min_len=0.01, effect_type=None)
    dummy_effect.apply = MagicMock(side_effect=_apply)
    return dummy_effect


@pytest.fixture(scope="function")
def effect_applier(dummy_effect):
    graph = EffectGraph()
    graph.add_node(dummy_effect)
    return EffectApplier(
        max_intensity=20,
        easy_start=0,
        min_effect_length=0.1,
        effect_graph=graph,
    )


def test_effect_applier_skip(effect_applier, scene):
    effect_applier.max_intensity = 20
    effect_applier.intensity = 30
    effect_applier.feed_scene(scene)
    effect = effect_applier.effect_graph.effects[0]
    effect.apply.assert_not_called()


def test_effect_applier_applied(effect_applier, scene):
    effect_applier.intensity = 0
    effect_applier.feed_scene(scene)
    effect = effect_applier.effect_graph.effects[0]
    effect.apply.assert_called()
