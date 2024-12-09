from dataclasses import dataclass
from typing import List
from modele.point import Point
from modele.collector import Collector

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.patches import Polygon

@dataclass
class Balise(Point):
    def __init__(self, x: float, y: float, z: float = 0, name: str = None):
        super().__init__(x, y, z)
        self.name = name

    def get_name(self): return self.name

    def __repr__(self):
        repr = super().__repr__()
        repr = repr.replace('Point', 'Balise').replace(')', f", name='{self.name}')")
        return repr
    
class DatabaseBalise(Collector[Balise]):
    def __init__(self, balises: List[Balise] = []):
        super().__init__()
        for balise in balises:
            self.add(key=balise.get_name(),
                     value=balise) # association cle/valeur

    def plot(self, ax: Axes, color: str) -> Axes:
        def coordinates_triangles(x, y, size):
            coords = np.array([[x, y + size],
                               [x - size, y - size],
                               [x + size, y - size]])
            return coords

        size=0.005
        for name, balise in self.get_all().items():
            triangle = coordinates_triangles(balise.getX(), balise.getY(), size=size)
            polygon = Polygon(triangle, closed=True, fill=True, edgecolor=color, facecolor=color)

            ax.add_patch(polygon)
            ax.text(balise.getX(), balise.getY() - size*2, name, fontsize=8, ha='right')
        return ax