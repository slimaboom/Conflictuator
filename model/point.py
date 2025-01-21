from dataclasses import dataclass
from math import sqrt
from enum import Enum

class PointValue(Enum):
    MinX = 0
    MaxX = 1
    MinY = 0
    MaxY = 1
    MinZ = 0
    MaxZ = 1

    def __eq__(self, other):
        if isinstance(other, (int, float)):
            return self.value == other
        return super().__eq__(other)

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self.value < other
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, (int, float)):
            return self.value < other
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return self.value > other
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, (int, float)):
            return self.value >= other
        return NotImplemented
    
@dataclass(frozen=False)
class Point:
    def __init__(self, x: float, y: float, z: float = 0):
        """
        Initialise un point normalisé en 3D.
        - x: abscisse normalisée entre -1 et 1.
        - y: ordonnée normalisée entre -1 et 1.
        - altitude: Altitude normalisée entre 0 et 1.
        """
        
        if not (PointValue.MinX.value <= x <= PointValue.MaxX.value):
            if x < 2 : 
                round(x,1)
            else:
                raise ValueError("abscisse normalisée doit être entre 0 et 1.")
        if not (PointValue.MinY.value <= y <= PointValue.MaxY.value):
            if y < 2 : 
                round(y,1)
            else:
                raise ValueError("ordonnée normalisée doit être entre 0 et 1.")
        if not (PointValue.MinZ.value <= z <= PointValue.MaxZ.value):
            raise ValueError("Altitude normalisée doit être entre 0 et 1.")
        self.x = x
        self.y = y
        self.z = z

    def getX(self): return self.x
    def getY(self): return self.y
    def getZ(self): return self.z

    def getXYZ(self): return self.getX(), self.getY(), self.getZ()
    def getXY(self): return self.getX(), self.getY()

    def distance(self, other: 'Point') -> float:
        """
        Calcule une distance approximative en espace normalisé.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return sqrt(dx*dx + dy*dy + dz*dz)
    
    def distance_horizontale(self, other: 'Point') -> float:
        """
        Calcule une distance horizontale en espace normalisé.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        dz = 0.
        return sqrt(dx*dx + dy*dy + dz*dz)

    def __repr__(self):
        """
        Représentation lisible du point.
        """
        return f"Point(x={self.x:.5f}, y={self.y:.5f}, z={self.z:.5f})"