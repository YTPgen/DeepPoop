from typing import List
import copy

import deep_poop.effects as effects
from deep_poop.effects.effect import EffectLengthDistribution


def set_bidirectional(effect_list: List[effects.Effect]):
    for current_effect in effect_list:
        for neighbor, val in copy.copy(current_effect.get_neighbors()).items():
            effects_with_name = [e for e in effect_list if e.name == neighbor]
            for e in effects_with_name:
                e.set_neighbor(effect_type=current_effect.name, weight=val)
    return effect_list


# TODO: Fix effects to not go back to previous ones unless so configured

EFFECTS = [
    effects.Scramble(
        min_scramble_frame_length=1,
        max_scramble_frame_length=3,
        unique_scramble=False,
        intensity=3,
        min_len=0.5,
        max_len=2.0,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=True,
        neighbors={"Zoom": 1, "Invert": 0.3},
    ),
    effects.Pixelate(
        min_strength=4,
        max_strength=12,
        intensity=1.7,
        max_len=4,
        length_distribution=EffectLengthDistribution.RANDOM,
        neighbors={"StretchX": 1},
        standalone=False,
    ),
    effects.Zoom(
        min_factor=0.4,
        max_factor=3,
        intensity=0.8,
        min_len=0.3,
        max_len=3.0,
        length_distribution=EffectLengthDistribution.RANDOM,
        neighbors={"Rotate": 1, "Invert": 2},
    ),
    effects.Zoom(
        min_factor=5,
        max_factor=9,
        intensity=0.8,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        neighbors={"Rotate": 1, "Invert": 2},
        name="QuickZoom",
    ),
    effects.Zoom(
        min_factor=2.5,
        max_factor=6,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        zoom_y=False,
        neighbors={"Echo": 1},
        name="StretchX",
    ),
    effects.Zoom(
        min_factor=2.5,
        max_factor=6,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        zoom_x=False,
        name="StretchY",
    ),
    effects.Echo(
        delay=0.1,
        strength=0.7,
        intensity=1.4,
        max_len=5,
        length_distribution=EffectLengthDistribution.NORMAL,
        neighbors={"Rotate": 1},
    ),
    effects.Invert(
        intensity=1.8,
        max_len=2.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        standalone=False,
        neighbors={"Echo": 1},
    ),
    effects.Rotate(
        min_speed=0.2,
        max_speed=2.5,
        center_on_face=False,
        intensity=1.4,
        max_len=1.2,
        length_distribution=EffectLengthDistribution.RANDOM,
    ),
]

EFFECTS = set_bidirectional(EFFECTS)
