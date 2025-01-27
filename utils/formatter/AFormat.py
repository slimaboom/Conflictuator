from abc import abstractmethod
from typing import List, TYPE_CHECKING
from typing_extensions import override

from utils.formatter.IFormat import IFormat
from utils.dynamic_discover_packages import dynamic_discovering

import inspect


if TYPE_CHECKING:
    from model.aircraft import Aircraft

class AFormat(IFormat):
    """Class abstraites pour les formats de données gérant une base de données des différents formats disponibles"""
    __registry = {}  # Stocke tous les formats disponibles (clé: nom, valeur: classe)
    
    @override
    def __init__(self):
        super().__init__()

    @abstractmethod
    def export(self, iterable: List['Aircraft']) -> str:
        """Renvoie l'export de la liste des Aircraft dans une chaine de caractère correspond au format souhaité"""
        pass

    @classmethod
    def register_format(cls, name: str):
        """Classe décoratrice pour enregistrer un nouveau format."""
        def decorator(subclass):
            # Vérifie que le constructeur (init) n'accepte que `self`
            init_signature = inspect.signature(subclass.__init__)
            if len(init_signature.parameters) > 1:  # Plus que `self`
                error =  f"La classe {subclass.__name__} ne peut pas avoir de paramètres dans son constructeur."
                raise TypeError(error)
            
            lower = name.lower()
            cls.__registry[lower] = subclass
            return subclass
        return decorator

    @classmethod
    def create_formatter(cls, name: str) -> 'AFormat':
        """
        Instancie une classe format à partir de son nom enregistré.
        """
        lower = name.lower()
        if lower not in cls.__registry:
            error = f"Format '{lower}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_format('{lower}') en décoration de la classe dérivée pour enregistré le format."
            raise ValueError(error)
        return cls.__registry[name]()

    @classmethod
    def get_available_formats(cls) -> List[str]:
        """
        Retourne tous les formats disponibles.
        """
        return list(cls.__registry.keys())

    @classmethod
    def discover_formatters(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les writters (ex. 'utils.writter').
        """
        dynamic_discovering(package=package, filename=__file__)