import deep_poop.effects as effects
from deep_poop.effects.effect import EffectLengthDistribution

EFFECTS = [
    effects.Scramble(
        scramble_frame_length=1,
        unique_scramble=False,
        intensity=4,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=True,
    ),
    effects.Echo(
        delay=0.1,
        strength=0.7,
        intensity=1.4,
        max_len=5,
        length_distribution=EffectLengthDistribution.NORMAL,
    ),
    effects.Invert(
        intensity=1.8, max_len=2.5, length_distribution=EffectLengthDistribution.RANDOM,
    ),
    effects.Pixelate(
        strength=10,
        intensity=1.7,
        max_len=4,
        length_distribution=EffectLengthDistribution.RANDOM,
    ),
    effects.Rotate(
        speed=3,
        center_on_face=False,
        intensity=1.4,
        max_len=2,
        length_distribution=EffectLengthDistribution.RANDOM,
    ),
]
