from enum import Enum


class SpeedValue(Enum):
    MAX: float = 1e-3
    MIN: float = 1e-5
    STEP: float = 1e-5