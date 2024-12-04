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
        # Récupérer la figure à partir de l'axe 
        for name, points in self.get_all().items():
            xy = [(p.x, p.y) for p in points]
            xymean = np.mean(xy, axis=0)
            polygon = Polygon(np.array(xy), closed=True, fill=True, edgecolor='black', linestyle='--', facecolor=color, alpha=0.5)
            ax.add_patch(polygon)
            #ax.text(xymean[0], xymean[1], s=name)
        return ax
    
"""
Flightroutes = [invert_y(route) for route in [
    [(0.02625, 0), (0.07, 0.29625), (0.07875, 0.69125), (0.06875, 0.81875), (0.05875, 0.99375)],
    [(0.30375, 0), (0.43875, 0.28625), (0.51625, 0.36875), (0.63375, 0.5975), (0.835, 0.99625)],
    [(0.715, 0.00125), (0.77625, 0.1125), (0.96625, 0.46625), (0.99875, 0.52625)],
    [(0.7375, 0), (0.5325, 0.19375), (0.4375, 0.2825), (0.2425, 0.5), (0.16625, 0.5925), (0.0775, 0.6925), (0.00125, 0.7575)],
    [(0.89125, 0.0025), (0.77375, 0.11125), (0.515, 0.37), (0.39875, 0.69), (0.4175, 0.99375)],
    [(-0.00125, 0.15375), (0.07, 0.29375), (0.2425, 0.5), (0.395, 0.6875), (0.82375, 0.97875), (0.85625, 0.99375)],
    [(0, 0.84375), (0.0675, 0.8175), (0.39625, 0.69), (0.63375, 0.59375), (0.80625, 0.52875), (0.96625, 0.465), (0.99625, 0.45)],
    [(0.72375, 0.7725), (0.99625, 0.9075)],
]]

def plot_sector():
    fig, ax = plt.subplots(figsize=(20,15))

    # Plot the main sector
    polygon = Polygon(ptsSectorMain, closed=True, fill=True, edgecolor='r', facecolor='#3B3B3BFF')
    ax.add_patch(polygon)

    # Plot secondary sectors with colors
    for sector in SectorsSecondary:
        sector_pts = invert_y(sector)
        polygon = Polygon(sector_pts, closed=True, fill=True, edgecolor='g', facecolor='#00000040')
        ax.add_patch(polygon)

    # Plot flight routes
    for route in Flightroutes:
        xs, ys = zip(*route)
        ax.plot(xs, ys, marker='o', color='gray', linestyle='-', linewidth=1, alpha=0.5)

    # Plot beacons
    for beacon in Beaconlist:
        ax.plot(beacon[0], 1-beacon[1], 'bo')
        ax.text(beacon[0], 1-beacon[1], beacon[2], fontsize=12, ha='right')

    plt.xlim(-0.25, 1.25)
    plt.ylim(-0.25, 1.25)
    #plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

plot_sector()
"""