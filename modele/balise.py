from dataclasses import dataclass
from typing import List, Dict
from modele.point import Point
from modele.collector import Collector

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.patches import Polygon
from copy import deepcopy
from logging_config import setup_logging

@dataclass
class Balise(Point):
    def __init__(self, x: float, y: float, z: float = 0, name: str = None):
        super().__init__(x, y, z)
        self.name = name
        self.conflits = []
        self.logger = setup_logging(__class__.__name__)

    def get_name(self) -> str: return self.name

    def __repr__(self):
        repr = super().__repr__()
        repr = repr.replace('Point', 'Balise').replace(')', f", name='{self.name}')")
        return repr
    
    def add_conflicts(self, conflicts) -> None:
        self.logger.info(f"Adding/Replacing conflict in balise: {self}\nfrom {self.conflits} to {conflicts}")
        self.conflits = conflicts # Ajoute les conflits

    
    def get_conflicts(self) -> List[Dict[str, float]]: return self.conflits

    def clear_conflicts(self, time: float) -> None: 
        self.logger.info(f"Clearing conflict in balise: {self}")
    
        filter_conflict = []
        for c in self.conflits:
            time_of_conflict = float(c.get('time_1'))
            if time_of_conflict < time:
                filter_conflict.append(c)
        
        self.conflits = filter_conflict
    
    def deepcopy(self) -> 'Balise':
        new_aircraft = deepcopy(self)
        return new_aircraft        

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