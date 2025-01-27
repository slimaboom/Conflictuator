from abc import ABC, abstractmethod
from enum import Enum
from algorithm.storage import DataStorage
from model.aircraft import Aircraft

from utils.controller.argument import method_control_type

from typing import List, Any
from typing_extensions import override
class VariableName(Enum):
    SPEED: int = 1
    TIME:  int = 2
    #HEADING: int = 3

class ISimulatedObject(ABC):
    """Interface pour l'objet utilisé lors d'un algorithme"""

    @abstractmethod
    def __init__(self, obj: Any):
        """Constructeur abstrait obligeant à passer un paramètre."""
        pass
    
    @abstractmethod 
    def update_commands(self, commands:List[DataStorage]) -> None:
        """Met a jour les commandes pour l'objet"""
        pass
    
    @abstractmethod
    def initialize(self) -> List[DataStorage]:
        """Initialise les commandes aleatoirement pour l'objet"""
        pass

    @abstractmethod
    def generate_neighbor(self) -> None:
        """Génère un voisin pour l'objet dans l'algorithme"""
        pass
    
    @abstractmethod
    def generate_commands(self) -> List[DataStorage]:
        """Renvoie une liste de DataStorage tiree aleatoirement representant les commandes de l'objet"""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """Representation de l'objet dans le contexte"""
        pass

    @abstractmethod
    def get_data_storages(self) -> List[DataStorage]:
        """Storage des donnees de l'objet necessaire lors de l'algorithme"""
        pass

    @abstractmethod
    def get_object(self) -> Any:
        """Retourne l'objet passé au constructeur."""
        pass


class ASimulatedAircraft(ISimulatedObject):
    """Classe abstraite pour l'objet utilisé lors d'un algorithme"""

    @override
    @method_control_type(Aircraft)
    def __init__(self, aircraft: Aircraft):
        """Constructeur abstrait obligeant à passer un paramètre."""
        self.__aircraft = aircraft
    
    @override
    def get_object(self) -> 'Aircraft':
        """Retourne l'avion passer en paramètre du constructeur"""
        return self.__aircraft
    
    def update_conflicts(self) -> None:
        """Met a jour les conflits de l'avion"""
        self.__aircraft.update_conflicts()