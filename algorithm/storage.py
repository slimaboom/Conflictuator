from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DataStorage:
    speed: float
    id: int
    time: Optional[float] = None
    heading: Optional[float] = None