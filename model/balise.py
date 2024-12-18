from dataclasses import dataclass
from typing import List, Dict
from model.point import Point
from model.collector import Collector

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
        #self.logger.info(f"Adding/Replacing conflict in balise: {self}\nfrom {self.conflits} to {conflicts}")
        self.conflits = conflicts # Ajoute les conflits

    
    def get_conflicts(self) -> List[Dict[str, float]]: return self.conflits

    def clear_conflicts(self, time: float) -> None: 
        #self.logger.info(f"Clearing conflict in balise: {self}")
    
        filter_conflict = []
        for c in self.conflits:
            time_of_conflict = float(c.get('time_1'))
            if time_of_conflict < time:
                filter_conflict.append(c)
        
        self.conflits = filter_conflict
    
    def deepcopy(self) -> 'Balise':
        new_balise = deepcopy(self)
        return new_balise        

class DatabaseBalise(Collector[Balise]):
    def __init__(self, balises: List[Balise] = []):
        super().__init__()
        for balise in balises:
            self.add(key=balise.get_name(),
                     value=balise) # association cle/valeur