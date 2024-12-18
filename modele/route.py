from modele.collector import Collector
from modele.balise import DatabaseBalise, Balise

from matplotlib.pyplot import Axes

from typing import List

class Airway(Collector[List[str]]):
    def __init__(self, name: str = None, points: List[str] = None):
        super().__init__(name, points)

    def plot(self, ax: Axes, balises: DatabaseBalise, color: str) -> Axes:
        for route_name, balise_names in self.get_all().items():
            balise_on_route = [balises.get_from_key(balise_name) for balise_name in balise_names]
            xs, ys = zip(*[p.getXY() for p in balise_on_route])
            ax.plot(xs, ys, marker='None', color=color, linestyle='-', linewidth=1, alpha=0.5)
        return ax
    
    @staticmethod
    def transform(routes: List[str], balises: DatabaseBalise, reverse: bool=False) -> List[Balise]:
        points = [balises.get_from_key(waypoint) for waypoint in routes]
        if reverse:
            points = list(reversed(points))
        return points