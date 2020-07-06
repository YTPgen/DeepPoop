import pytest
import os

from moviepy.editor import VideoFileClip

from deep_poop.scene import Scene
from deep_poop.effects.effect import Effect, ImageEffect
from deep_poop.effects import Echo, Invert, Pixelate, Rotate, Scramble

test_clip_name = "slice_lemon.mp4"
current_dir = os.path.dirname(os.path.abspath(__file__))
test_clip = os.path.join(current_dir, "clips", test_clip_name)


@pytest.fixture(scope="session")
def clip():
    return VideoFileClip(test_clip)


@pytest.fixture(scope="session")
def scene():
    s = Scene(video_file=test_clip, start=0.0, end=3.0)
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
    return Pixelate(strength=5, intensity=1)


@pytest.fixture(scope="session")
def rotate():
    return Rotate(speed=3, intensity=1)


@pytest.fixture(scope="session")
def scramble():
    return Scramble(scramble_frame_length=3, intensity=1)
