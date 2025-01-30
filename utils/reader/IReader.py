from abc import ABC, abstractmethod

class IReader(ABC):
    """Interface pour les classes qui lisent des données."""

    @abstractmethod
    def __init__(self, source: str):
        """Constructeur avec un seul paramètre correspondant la source pour lire les donnée.
        Exemple: fichier, base de donnée
        """
        pass

    @abstractmethod
    def read(self) -> str:
        """Lit des données et retourne une chaîne formatée."""
        pass
