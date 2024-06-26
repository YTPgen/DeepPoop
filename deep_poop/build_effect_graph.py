from deep_poop.value_generator import ConstantValueGenerator, RandomValueGenerator
from deep_poop.effects.interpolator import InterpolationType, StrengthInterpolator
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
        min_len=0.5,
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
        min_len=0.3,
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
        min_len=0.3,
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
        interpolator=StrengthInterpolator(interpolation_type=InterpolationType.NONE),
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
        interpolator=StrengthInterpolator(interpolation_type=InterpolationType.NONE),
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
        interpolator=StrengthInterpolator(
            max_points_amount=10,
            max_points_per_second=2,
            max_y=2,
            min_y=0.5,
            interpolation_type=InterpolationType.CUBIC,
        ),
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
        interpolator=StrengthInterpolator(interpolation_type=InterpolationType.NONE),
        zoom_y=False,
        name="StretchX",
    )
)

rubber_stretch_x = add(
    effects.Zoom(
        min_factor=2.5,
        max_factor=10,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        interpolator=StrengthInterpolator(
            max_points_amount=20,
            max_points_per_second=3,
            interpolation_type=InterpolationType.CUBIC,
        ),
        zoom_y=False,
        name="RubberStretchX",
    )
)


rubber_stretch_y = add(
    effects.Zoom(
        min_factor=2.5,
        max_factor=10,
        intensity=1.3,
        min_len=0.3,
        max_len=1.5,
        length_distribution=EffectLengthDistribution.RANDOM,
        interpolator=StrengthInterpolator(
            max_points_amount=20,
            max_points_per_second=3,
            interpolation_type=InterpolationType.CUBIC,
        ),
        zoom_x=False,
        name="RubberStretchY",
    )
)

face_swirl = add(
    effects.Swirl(
        intensity=1,
        min_len=0.5,
        max_len=3,
        min_swirl=2,
        max_swirl=13,
        radius_generator=RandomValueGenerator(0.1, 0.3),
        center_on_face=True,
        transition_time_generator=RandomValueGenerator(0, 2),
        name="FaceSwirl",
    )
)

inflate = add(
    effects.Bulge(
        intensity=0.7,
        min_len=0.5,
        max_len=3,
        min_bulge=1.5,
        max_bulge=4,
        center_on_face=True,
        radius_generator=RandomValueGenerator(0.1, 0.4),
        transition_time_generator=RandomValueGenerator(0, 1),
        name="Inflate",
    )
)

black_hole = add(
    effects.Bulge(
        intensity=1.2,
        min_len=0.5,
        max_len=3,
        min_bulge=5,
        max_bulge=10,
        center_on_face=True,
        interpolator=StrengthInterpolator(min_points_amount=2, max_points_amount=5),
        radius_generator=RandomValueGenerator(0.1, 0.4),
        transition_time_generator=RandomValueGenerator(0, 2.5),
        name="BlackHole",
    )
)


# deflate = add(
#     effects.Bulge(
#         intensity=1.2,
#         min_bulge=1.5,
#         max_bulge=3,
#         invert=True,
#         center_on_face=True,
#         radius_generator=RandomValueGenerator(0.1, 0.2),
#         transition_time_generator=RandomValueGenerator(0, 1.2),
#         name="Deflate",
#     )
# )


###############
# SOUND
###############

echo = add(
    effects.Echo(
        delay=0.05,
        intensity=1.4,
        min_len=2,
        max_len=3.7,
        length_distribution=EffectLengthDistribution.NORMAL,
    )
)

pitch_up = add(
    effects.Pitch(
        min_steps=7,
        max_steps=18,
        min_len=0.5,
        max_len=2.5,
        intensity=1.4,
        name="PitchUp",
    ),
)
pitch_down = add(
    effects.Pitch(
        min_steps=-4,
        max_steps=-15,
        min_len=0.7,
        max_len=3.2,
        intensity=1.0,
        name="PitchDown",
    )
)
space_robot = add(
    effects.OscillatingRobotify(
        min_freq=2,
        max_freq=300,
        min_oscillation=50,
        max_oscillation=500,
        min_len=2,
        max_len=4,
        intensity=1.5,
        name="SpaceRobotify",
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

connect(zoom_out, shake, 1)

connect(quick_zoom, rotate, 2)
connect(quick_zoom, invert, 1)
connect(quick_zoom, scramble, 2)

connect(pitch_up, pixelate, 1)
connect(pitch_down, invert, 0.5)
connect(space_robot, scramble, 0.5)

connect(robotify, invert, 0.7)
connect(robotify, pixelate, 1)

connect(invert, echo, 0.4)

connect(rubber_stretch_y, shake, 1)
connect(rubber_stretch_y, pitch_down, 1.5)
connect(rubber_stretch_y, rotate, 1)

connect(rubber_stretch_x, pitch_down, 1)
connect(rubber_stretch_x, rotate, 1)

connect(inflate, pitch_up, 1)
connect(inflate, pitch_down, 1)
connect(inflate, zoom_out, 1)
# connect(deflate, pitch_down, 1)

connect(black_hole, space_robot, 1)
connect(black_hole, shake, 1.2)
connect(black_hole, scramble, 1.2)

connect(face_swirl, zoom, 1)
connect(face_swirl, pitch_down, 1)
connect(face_swirl, shake, 1)

EFFECT_GRAPH = graph
