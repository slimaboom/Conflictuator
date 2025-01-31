from abc import ABC, abstractmethod
from typing import Dict
from model.aircraft.aircraft import Aircraft

class ITrafficGenerator(ABC):
    """Interface imposant l'implémentation de generate_traffic()."""
    
    @abstractmethod
    def generate_traffic(self) -> Dict[int, Aircraft]:
        """Génère un trafic aérien sous forme de dictionnaire {id: Aircraft}."""
        pass

    @abstractmethod
    def get_simulation_duration(self) -> float:
        """Renvoie la durée de la simulation"""
        pass
