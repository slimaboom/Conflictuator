from enum import Enum


class SpeedValue(Enum):
    MAX: float = 0.002   # 8 min = 1 unité = traversé le domain
    MIN: float = 0.0010  # 15 min = 1 unité = traversé le domain
    STEP: float = 1e-5

# np.round(np.linspace(0.000138, 0.0016, 20), 6) 
# array([0.000138, 0.000215, 0.000292, 0.000369, 0.000446, 0.000523,
#        0.0006  , 0.000677, 0.000754, 0.000831, 0.000907, 0.000984,
#        0.001061, 0.001138, 0.001215, 0.001292, 0.001369, 0.001446,
#        0.001523, 0.0016  ])