from collector import Collector
from balise import DatabaseBalise

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.patches import Polygon

from typing import List

class Airway(Collector[List[str]]):
    def __init__(self, name: str = None, points: List[str] = None):
        super().__init__(name, points)

    def plot(self, ax: Axes, balises: DatabaseBalise, color: str) -> Axes:
        for route_name, balise_names in self.get_all().items():
            balise_on_route = [balises.get_from_key(balise_name) for balise_name in balise_names]
            xs, ys = zip(*[(p.x, p.y) for p in balise_on_route])
            ax.plot(xs, ys, marker='None', color=color, linestyle='-', linewidth=1, alpha=0.5)
        return ax