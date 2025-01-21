from abc import ABC, abstractmethod
from algorithm.recuit.data import ISimulatedObject
from algorithm.storage import DataStorage
from typing import List, Optional

# Interface 
class IObjective(ABC):

    @abstractmethod
    def evaluate(self, data: List[ISimulatedObject], individual: Optional[List[List[DataStorage]]] = None) -> float:
        """Calcule la fitness d'un individu."""
        pass
