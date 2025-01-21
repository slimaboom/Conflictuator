from abc import ABC, abstractmethod
from algorithm.recuit.data import ISimulatedObject
from typing import List

# Interface 
class IObjective(ABC):
    @abstractmethod
    def evaluate(self, data: List[ISimulatedObject]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass