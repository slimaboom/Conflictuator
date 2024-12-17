from model.collector import Collector
from model.point import Point

from enum import Enum

from typing import List

class SectorType(Enum):
    MAIN: str = "MAIN_SECTOR"
    SECONDARY: str = "SECONDARY_SECTORY"

class Sector(Collector[List[Point]]):
    def __init__(self, name: str = None, points: List[Point] = None):
        super().__init__(name, points)