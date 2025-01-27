from abc import ABC, abstractmethod
from typing import Any

class IFormat(ABC):
    """Interface pour les formats de données"""
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def export(self, obj: Any) -> str:
        """Renvoie l'export de l'objet <obj> dans une chaine de caractère correspond au format souhaité"""
        pass