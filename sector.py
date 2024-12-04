from collector import Collector
from point import Point

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.patches import Polygon

from typing import List

class Sector(Collector[List[Point]]):
    def __init__(self, name: str = None, points: List[Point] = None):
        super().__init__(name, points)

    def plot(self, ax: Axes, color: str) -> Axes:
        for name, points in self.get_all().items():
            xy = [(p.x, p.y) for p in points]
            xymean = np.mean(xy, axis=0)
            polygon = Polygon(np.array(xy), closed=True, fill=True, edgecolor='black', linestyle='--', facecolor=color, alpha=0.5)
            ax.add_patch(polygon)
            #ax.text(xymean[0], xymean[1], s=name)
        return ax
    

# Plot flight routes
#for route in Flightroutes:
#xs, ys = zip(*route)
#ax.plot(xs, ys, marker='o', color='gray', linestyle='-', linewidth=1, alpha=0.5)"""