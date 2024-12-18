from abc import ABC, abstractmethod
from dataclasses import dataclass
from model.aircraft import Aircraft, SpeedValue
import numpy as np

@dataclass(frozen=True)
class DataStorage:
    speed: float
    id: int

class ISimulatedObject(ABC):
    """Classe d'interface pour l'objet utilisé lors du recuit simulé"""
    
    @abstractmethod
    def update(self, value: float) -> None:
        """Met à jour l'objet pour le recuit"""
        pass
    
    @abstractmethod
    def generate_neighbor(self) -> None:
        """Génère un voisin pour l'objet dans l'algorithme de recuit"""
        pass
    
    @abstractmethod
    def evaluate(self) -> float:
        """Évalue l'objet dans le contexte du recuit simulé"""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Representation de l'objet dans le contexte du recuit simulé"""
        pass

    @abstractmethod
    def get_data_storage(self) -> DataStorage:
        """Storage des donnees de l'objet necessaire lors du recuit simulé"""
        pass


class SimulatedAircraftImplemented(ISimulatedObject):
    """Implémentation concrète de ISimulatedObject"""
    
    def __init__(self, aircraft: Aircraft):
        self.aircraft = aircraft
        self.random_generator = self.aircraft.get_random_generator()

        self.possible_speeds = [0.001, 0.002, 0.003, 0.0012]#np.linspace(SpeedValue.MIN.value, SpeedValue.MAX.value, 20)

    def update(self, value: float) -> None:
        """Mise à jour de la vitesse dans le cadre du recuit"""
        self.aircraft.set_speed(value)
    
    def generate_neighbor(self) -> None:
        """Génère un voisin pour l'avion simulé"""
        # Exemple d'une nouvelle vitesse aléatoire
        new_speed = self.random_generator.choice(self.possible_speeds)
        self.update(round(new_speed, 4))
    
    def evaluate(self) -> float:
        """Évaluation du critère pour le recuit simulé"""
        conflicts = self.aircraft.get_conflicts()
        return len(conflicts)

    def __repr__(self):
        return f"Aircraft(id={self.aircraft.get_id_aircraft()}, speed={self.aircraft.get_speed()})"

    def get_data_storage(self) -> DataStorage:
        """Storage des donnees de l'objet necessaire lors du recuit simulé"""
        return DataStorage(self.aircraft.get_speed(), self.aircraft.get_id_aircraft())