import enum
import random
from typing import List

from deep_poop.scene import Scene
from scipy import interpolate


class InterpolationType(enum.Enum):
    NONE = "none"
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    CUBIC = "cubic"


MIN_POINTS = {
    InterpolationType.NONE: 0,
    InterpolationType.LINEAR: 2,
    InterpolationType.QUADRATIC: 3,
    InterpolationType.CUBIC: 4,
}


class StrengthInterpolator:
    def __init__(
        self,
        min_points_amount: int = 4,
        max_points_amount: int = 5,
        max_points_per_second: int = 1,
        min_y: float = 0.05,
        max_y: float = 1,
        interpolation_type: InterpolationType = InterpolationType.LINEAR,
    ):
        self.min_point_amount = min_points_amount
        self.max_point_amount = max_points_amount
        self.max_points_per_second = max_points_per_second
        self.min_y = min_y
        self.max_y = max_y
        self.interpolation_type = interpolation_type

    def generate(self, scene: Scene = None):
        if self.interpolation_type == InterpolationType.NONE:
            return
        x = []
        y = []
        if self.min_y > self.max_y:
            raise ValueError("Min y larger than maximum")
        if self.min_point_amount >= self.max_point_amount:
            raise ValueError("Min point amount larger than maximum")

        min_points = int(
            max(MIN_POINTS[self.interpolation_type], self.min_point_amount)
        )
        max_points = (
            self.max_point_amount
            if not scene
            else min(self.max_point_amount, scene.length() * self.max_points_per_second)
        )
        max_points = int(max(max_points, min_points))
        points_amount = random.randint(min_points, max_points)

        # Could support other than random distribution of points
        generate_y = lambda: random.random() * (self.max_y - self.min_y) + self.min_y

        # Add end and beginning of graph
        x.append(0)
        y.append(generate_y())
        x.append(1)
        y.append(generate_y())

        for i in range(points_amount - 2):
            x.append(random.random())
            y.append(generate_y())
        self._interpolatef = interpolate.interp1d(
            x, y, kind=self.interpolation_type.value
        )

    def interpolate_all_frames(self, scene: Scene):
        self.generate(scene)
        frames = scene.frames
        return self.interpolate_frames(list(range(len(frames))), len(frames))

    def interpolate_frames(
        self,
        frame_indices: List,
        total_frames: int,
    ):
        if self.interpolation_type == InterpolationType.NONE:
            return [1] * total_frames
        # normalize all indices to range 0-1
        for i in range(len(frame_indices)):
            frame_indices[i] = (frame_indices[i] + 1) / total_frames
        interpolated = self._interpolatef(frame_indices)
        for i in range(len(interpolated)):
            interpolated[i] = max(interpolated[i], self.min_y)
            interpolated[i] = min(interpolated[i], self.max_y)
        return interpolated
