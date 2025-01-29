from dataclasses import dataclass
from typing import List
from model.point import Point
from model.collector import Collector
from model.conflict_manager import ConflictInformation

from copy import deepcopy
from logging_config import setup_logging

@dataclass
class Balise(Point):
    def __init__(self, x: float, y: float, z: float = 0, name: str = None):
        super().__init__(x, y, z)
        self.name = name
        self.conflits: List[ConflictInformation] = []
        self.logger = setup_logging(__class__.__name__)

    def __hash__(self):
        return hash((self.x, self.y, self.z, self.name))

    def __eq__(self, other):
        if not isinstance(other, Balise):
            return False
        return (self.x, self.y, self.z, self.name) == (other.x, other.y, other.z, other.name)

    def get_name(self) -> str: return self.name

    def get_point(self) -> Point: return Point(self.x, self.y, self.z) 

    def __repr__(self):
        repr = super().__repr__()
        repr = repr.replace('Point', 'Balise').replace(')', f", name='{self.name}')")
        return repr
    
    def set_conflicts(self, conflicts: List[ConflictInformation]) -> None:
        #self.logger.info(f"Adding/Replacing conflict in balise: {self}\nfrom {self.conflits} to {conflicts}")
        self.conflits = conflicts # Ajoute les conflits

    def add_conflicts(self, conflict: ConflictInformation) -> None:
        #self.logger.info(f"Adding/Replacing conflict in balise: {self}\nfrom {self.conflits} to {conflicts}")
        if conflict not in self.conflits :
            self.conflits.append(conflict)  # Ajoute les conflits

    
    def get_conflicts(self) -> List[ConflictInformation]: return self.conflits

    def clear_conflicts(self, time: float) -> None: 
        #self.logger.info(f"Clearing conflict in balise: {self}")
    
        filter_conflict = []
        for c in self.conflits:
            time_of_conflict = min(c.get_conflict_time_one(), c.get_conflict_time_two())
            if time_of_conflict < time:
                filter_conflict.append(c)
        
        self.conflits = filter_conflict

    def clear_conflicts_between(self, aircraft_id_one: int, aircraft_id_two: int) -> None:
        """
        Supprime les conflits impliquant deux avions spécifiques identifiés par leurs IDs.

        Args:
            aircraft_id_one (int): ID du premier avion.
            aircraft_id_two (int): ID du second avion.
        """
        self.conflits = [
            conflict for conflict in self.conflits
            if not (
                (conflict.get_aircraft_one().get_id_aircraft() == aircraft_id_one and
                conflict.get_aircraft_two().get_id_aircraft() == aircraft_id_two)
                or
                (conflict.get_aircraft_one().get_id_aircraft() == aircraft_id_two and
                conflict.get_aircraft_two().get_id_aircraft() == aircraft_id_one)
            )
        ]

    
    def deepcopy(self) -> 'Balise':
        new_balise = deepcopy(self)
        return new_balise       
    


        

class DatabaseBalise(Collector[Balise]):
    def __init__(self, balises: List[Balise] = []):
        super().__init__()
        for balise in balises:
            self.add(key=balise.get_name(),
                     value=balise) # association cle/valeur
            