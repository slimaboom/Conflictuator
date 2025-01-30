from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DataStorage:
    id: int
    speed: float
    time: Optional[float] = None
    heading: Optional[float] = None