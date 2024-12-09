from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=False)
class Point:
    def __init__(self, x: float, y: float, z: float = 0):
        """
        Initialise un point normalisé en 3D.
        - x: abscisse normalisée entre -1 et 1.
        - y: ordonnée normalisée entre -1 et 1.
        - altitude: Altitude normalisée entre 0 et 1.
        """
        if not (0 <= x <= 1):
            raise ValueError("abscisse normalisée doit être entre 0 et 1.")
        if not (0 <= y <= 1):
            raise ValueError("ordonnée normalisée doit être entre 0 et 1.")
        if not (0 <= z <= 1):
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