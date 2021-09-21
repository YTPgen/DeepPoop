from deep_poop.effects.effect_graph import EffectGraph
import deep_poop.effects as effects
from deep_poop.effects.effect import EffectLengthDistribution


graph = EffectGraph(overwrite_connections=False)
add = graph.add_node
###############
#   VIDEO
###############

shake = add(
    effects.Shake(
        min_strength=4,
        max_strength=100,
        min_len=0.5,
        max_len=2.0,
        intensity=2.1,
    )
)
scramble = add(
    effects.Scramble(
        min_scramble_frame_length=1,
        max_scramble_frame_length=3,
        unique_scramble=False,
        intensity=3,
        min_len=1.5,
        max_len=2.0,
        length_distribution=EffectLengthDistribution.RANDOM,
        can_cut=False,
    )
)
pixelate = add(
    effects.Pixelate(
        min_strength=4,
        max_strength=12,
        intensity=4.7,
        max_len=1.2,
        length_distribution=EffectLengthDistribution.RANDOM,
        standalone=False,
    )
)
rotate = add(
    effects.Rotate(
        min_speed=0.2,
        max_speed=2.5,
        center_on_face=False,
        intensity=1.4,
        max_len=1.2,
        length_distribution=EffectLengthDistribution.RANDOM,
    )
)

###############
#   ZOOM / STRETCH
###############

zoom = add(
    effects.Zoom(
        min_factor=1.8,
        max_factor=3,
        intensity=0.8,
        min_len=0.3,
        max_len=3.0,
        length_distribution=EffectLengthDistribution.RANDOM,
    )
)
zoom_out = add(
    effects.Zoom(
        min_factor=0.1,
        max_factor=0.5,
        intensity=1.7,
        min_len=0.3,
        max_len=2.0,
        name="ZoomOut",
    )
)
quick_zoom = add(
    effects.Zoom(
        min_factor=5,
        max_factor=9,
        intensity=0.8,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        name="QuickZoom",
    )
)
stretch_x = add(
    effects.Zoom(
        min_factor=2.5,
        max_factor=6,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        zoom_y=False,
        name="StretchX",
    )
)
stretch_y = add(
    effects.Zoom(
        min_factor=2.5,
        max_factor=6,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        zoom_x=False,
        name="StretchY",
    )
)

###############
# SOUND
###############

echo = add(
    effects.Echo(
        delay=0.1,
        strength=0.7,
        intensity=1.4,
        min_len=2,
        max_len=3.7,
        length_distribution=EffectLengthDistribution.NORMAL,
    )
)

pitch_up = add(
    effects.Pitch(
        min_steps=7,
        max_steps=30,
        min_len=1.2,
        max_len=2.5,
        intensity=1.4,
        name="PitchUp",
    ),
)
pitch_down = add(
    effects.Pitch(
        min_steps=-7,
        max_steps=-20,
        min_len=1.7,
        max_len=3.2,
        intensity=1.0,
        name="PitchDown",
    )
)
oscillating_robotify = add(
    effects.OscillatingRobotify(
        min_freq=2,
        max_freq=300,
        min_oscillation=50,
        max_oscillation=500,
        min_len=2,
        max_len=4,
        intensity=1.5,
    )
)
robotify = add(
    effects.Robotify(
        min_freq=2,
        max_freq=20,
        min_len=1,
        max_len=4,
        intensity=1.4,
    )
)

###########
# IMAGE EFFECTS
###########
invert = add(
    effects.Invert(
        intensity=2.8,
        min_len=1,
        max_len=2,
        length_distribution=EffectLengthDistribution.RANDOM,
        standalone=False,
    )
)

# Setup graph connections

connect = graph.add_connection


connect(shake, zoom, 1)
connect(shake, echo, 0.7)
connect(shake, robotify, 1)

connect(scramble, zoom, 1)
connect(scramble, invert, 0.3)

connect(pixelate, stretch_x, 1)
connect(pixelate, pitch_down, 1)

connect(rotate, zoom, 1)

connect(zoom, invert, 1)

connect(zoom_out, shake, 1)

connect(quick_zoom, rotate, 1)
connect(quick_zoom, invert, 2)

connect(stretch_x, echo, 1)
connect(stretch_y, shake, 1)

connect(pitch_up, pixelate, 1)
connect(oscillating_robotify, invert, 1.5)
connect(oscillating_robotify, scramble, 1)
connect(oscillating_robotify, stretch_y, 1.5)

connect(robotify, invert, 1)
connect(robotify, pixelate, 2)
connect(robotify, stretch_y, 1.35)

connect(invert, echo, 1)

EFFECT_GRAPH = graph