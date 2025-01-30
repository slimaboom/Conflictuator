from enum import Enum


class SpeedValue(Enum):
    MAX: float = 1e-2
    MIN: float = 1e-4
    STEP: float = 1e-4