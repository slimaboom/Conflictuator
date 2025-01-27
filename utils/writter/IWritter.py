from abc import ABC, abstractmethod
from typing import Any

class IWritter(ABC):
    """Interface pour les classes qui écrivent des données"""
    @abstractmethod
    def __init__(self, container: str):
        """Constructeur avec un seul paramètre correspondant à où l'écriture va se faire (fichier, base de donnée)"""
        pass

    @abstractmethod
    def write(self, text: str) -> bool:
        """Renvoie True si l'écriture du <texte> a été possible et False sinon"""
        pass