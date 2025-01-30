from abc import ABC, abstractmethod
from typing import Any

class IReader(ABC):
    """Interface pour lire des données"""
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def export(self, obj: Any) -> str:
        """Renvoie l'export de l'objet <obj> dans une chaine de caractère correspond au format souhaité"""
        pass