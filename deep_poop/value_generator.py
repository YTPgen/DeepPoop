import abc
import math
import random


class ValueGenerator:
    """Helper class for generating values in a distribution.
    Useful for effects that have varying values on each application.

    """

    def __init__(self, round_fn=math.floor):
        self.round_fn = round_fn

    @abc.abstractmethod
    def generate(self) -> float:
        """Generates a float number. To be implemented by child class.

        Returns:
            float: Generated value
        """
        raise NotImplementedError

    def generate_int(self) -> int:
        """Generates an int number rounding with round_fn

        Returns:
            int: Generated int value
        """
        return self.round_fn(self.generate)


class ConstantValueGenerator(ValueGenerator):
    def __init__(self, value: float, *args, **kwargs):
        self.value = value
        super(ConstantValueGenerator, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    def generate(self) -> float:
        return self.value


class RandomValueGenerator(ValueGenerator):
    def __init__(self, min_val: float, max_val: float, *args, **kwargs):
        self.min_val = min_val
        self.max_val = max_val
        super(RandomValueGenerator, self).__init__(*args, **kwargs)

    @abc.abstractmethod
    def generate(self) -> float:
        return random.random() * (self.max_val - self.min_val) + self.min_val


ZERO = ConstantValueGenerator(0)
