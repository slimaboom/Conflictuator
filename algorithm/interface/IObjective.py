from abc import ABC, abstractmethod
from algorithm.interface.ISimulatedObject import ISimulatedObject, ASimulatedAircraft
from typing import List
from typing_extensions import override

# Interface 
class IObjective(ABC):
    """Interface pour le calcul d'une fonction objectif a partir d'une liste de ISimulatedObject"""
    
    @abstractmethod
    def evaluate(self, data: List[ISimulatedObject]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Nom pour decrire la fonction Objectif"""
        pass

# Abstraction
class AObjective(IObjective):
    """Classe abstraite pour le calcul d'une fonction objectif a partir d'une liste de ASimulatedAircraft"""

    @abstractmethod
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass

    @override
    def name(self) -> str:
        return f"{self.__class__.__name__}"
    