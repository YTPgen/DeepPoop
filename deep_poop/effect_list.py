import deep_poop.effects as effects
from deep_poop.effects.effect import EffectLengthDistribution

EFFECTS = [
    effects.Scramble(
        min_scramble_frame_length=1,
        max_scramble_frame_length=3,
        unique_scramble=False,
        intensity=3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=True,
        compatible_effects={effects.Pixelate: 1},
    ),
    effects.Echo(
        delay=0.1,
        strength=0.7,
        intensity=1.4,
        max_len=5,
        length_distribution=EffectLengthDistribution.NORMAL,
        compatible_effects={effects.Rotate: 1},
    ),
    effects.Invert(
        intensity=1.8,
        max_len=2.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        standalone=False,
        compatible_effects={effects.Echo: 1},
    ),
    effects.Pixelate(
        min_strength=4,
        max_strength=12,
        intensity=1.7,
        max_len=4,
        length_distribution=EffectLengthDistribution.RANDOM,
        compatible_effects={effects.Rotate: 1},
        standalone=False,
    ),
    effects.Rotate(
        min_speed=0.2,
        max_speed=2.5,
        center_on_face=False,
        intensity=1.4,
        max_len=2,
        length_distribution=EffectLengthDistribution.RANDOM,
    ),
]
