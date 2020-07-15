import pytest
import os

from moviepy.editor import VideoFileClip

from deep_poop.scene import Scene
from deep_poop.effects.effect import Effect, ImageEffect
from deep_poop.effects import Echo, Invert, Pixelate, Rotate, Scramble, Zoom

test_clip_name = "slice_lemon.mp4"
current_dir = os.path.dirname(os.path.abspath(__file__))
test_clip = os.path.join(current_dir, "clips", test_clip_name)


@pytest.fixture(scope="function")
def clip():
    return VideoFileClip(test_clip).subclip(0, 0.2)


@pytest.fixture(scope="function")
def scene(clip):
    s = Scene(video_clip=clip)
    s.analyze_frames()
    return s


@pytest.fixture(scope="session")
def test_effect():
    return Effect(intensity=1, effect_type=None)


###
# Effect fixtures
###


@pytest.fixture(scope="session")
def echo():
    return Echo(delay=1, strength=1, intensity=1)


@pytest.fixture(scope="session")
def invert():
    return Invert(intensity=1)


@pytest.fixture(scope="session")
def pixelate():
    return Pixelate(min_strength=3, max_strength=5, intensity=1)


@pytest.fixture(scope="session")
def rotate():
    return Rotate(min_speed=1, max_speed=1.5, intensity=1)


@pytest.fixture(scope="session")
def scramble():
    return Scramble(
        min_scramble_frame_length=1, max_scramble_frame_length=3, intensity=1
    )


@pytest.fixture(scope="function")
def zoom():
    return Zoom(min_factor=1.5, max_factor=2, center_on_face=False, intensity=1)
