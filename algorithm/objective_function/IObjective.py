from abc import ABC, abstractmethod
from algorithm.recuit.data import ISimulatedObject
from algorithm.storage import DataStorage
from typing import List, Optional

# Interface 
class IObjective(ABC):

    @abstractmethod
    def evaluate(self, data: List[ISimulatedObject]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass

class ObjectiveError(Exception):
    pass