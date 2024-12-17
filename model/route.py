from model.collector import Collector
from model.balise import DatabaseBalise, Balise

from typing import List

class Airway(Collector[List[str]]):
    def __init__(self, name: str = None, points: List[str] = None):
        super().__init__(name, points)
    
    @staticmethod
    def transform(routes: List[str], balises: DatabaseBalise, reverse: bool=False) -> List[Balise]:
        points = [balises.get_from_key(waypoint) for waypoint in routes]
        if reverse:
            points = list(reversed(points))
        return points