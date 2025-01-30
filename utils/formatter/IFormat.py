from abc import ABC, abstractmethod
from typing import Any

class IFormat(ABC):
    """Interface pour les formats de données"""

    @abstractmethod
    def export(self, obj: Any) -> str:
        """Renvoie l'export de l'objet <obj> dans une chaine de caractère correspond au format souhaité"""
        pass

    @abstractmethod
    def parse(self, data: str) -> Any:
        """Renvoie le parsing de l'argument <data> qui est une chaine en un objet Any"""
        pass