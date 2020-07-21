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


EFFECTS = [
    effects.Pitch(
        min_steps=7,
        max_steps=30,
        min_len=1.2,
        max_len=2.5,
        intensity=1.4,
        neighbors={"StretchY": 1, "ZoomOut": 1.5},
        name="PitchUp",
    ),
    effects.Pitch(
        min_steps=-7,
        max_steps=-20,
        min_len=1.7,
        max_len=3.2,
        intensity=1.0,
        neighbors={"Zoom": 1.5, "Invert": 1.5, "Pixelate": 2},
        name="PitchDown",
    ),
    effects.OscillatingRobotify(
        min_freq=2,
        max_freq=300,
        min_oscillation=50,
        max_oscillation=500,
        min_len=2,
        max_len=4,
        intensity=1.5,
        neighbors={"Invert": 1.5, "Scramble": 1, "StretchY": 1.5},
    ),
    effects.Robotify(
        min_freq=2,
        max_freq=20,
        min_len=1,
        max_len=4,
        intensity=1.4,
        neighbors={"Invert": 1, "Pixelate": 2, "StretchY": 1.35},
    ),
    effects.Shake(
        min_strength=4,
        max_strength=100,
        min_len=0.5,
        max_len=2.0,
        intensity=2.1,
        neighbors={"Zoom": 1, "Echo": 0.7, "Robotify": 1},
    ),
    effects.Scramble(
        min_scramble_frame_length=1,
        max_scramble_frame_length=3,
        unique_scramble=False,
        intensity=3,
        min_len=1.5,
        max_len=2.0,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=False,
        neighbors={"Zoom": 1, "Invert": 0.3},
    ),
    effects.Pixelate(
        min_strength=4,
        max_strength=12,
        intensity=4.7,
        max_len=1.2,
        length_distribution=EffectLengthDistribution.RANDOM,
        neighbors={"StretchX": 1},
        standalone=False,
    ),
    effects.Zoom(
        min_factor=1.8,
        max_factor=3,
        intensity=0.8,
        min_len=0.3,
        max_len=3.0,
        length_distribution=EffectLengthDistribution.RANDOM,
        neighbors={"Rotate": 1, "Invert": 2},
    ),
    effects.Zoom(
        min_factor=0.1,
        max_factor=0.5,
        intensity=1.7,
        min_len=0.3,
        max_len=2.0,
        name="ZoomOut",
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
        min_len=2,
        max_len=3.7,
        length_distribution=EffectLengthDistribution.NORMAL,
        neighbors={"Shake": 1},
    ),
    effects.Invert(
        intensity=2.8,
        min_len=1,
        max_len=2,
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
