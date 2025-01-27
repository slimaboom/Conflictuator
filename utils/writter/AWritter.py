from abc import abstractmethod
from typing import List
from typing_extensions import override

from utils.writter.IWritter import IWritter
from utils.dynamic_discover_packages import dynamic_discovering

import inspect


class AWritter(IWritter):
    """Classe abstraite pour les classes qui écrivent des données"""
    __registry = {}  # Stocke tous les formats disponibles (clé: nom, valeur: classe)

    @override
    def __init__(self, container: str):
        """Constructeur avec un seul paramètre correspondant à où l'écriture va se faire (fichier, base de donnée)"""
        super().__init__(container)
        self.__container = container

    @abstractmethod
    def write(self, text: str) -> bool:
        """Renvoie True si l'écriture du <texte> a été possible et False sinon"""
        pass
    
    def get_container(self) -> str: 
        """Chaine de caractères passée aux constructeur permettant de savoir où la classe écrit (fichier, base de donnée, ect)"""
        return self.__container

    @classmethod
    def register_writter(cls, name: str):
        """Classe décoratrice pour enregistrer un nouveau writter."""
        def decorator(subclass):
            # Vérifie que le constructeur (init) n'accepte que `self` et `container`
            init_signature = inspect.signature(subclass.__init__)
            if len(init_signature.parameters) > 2:  # Plus que `self` et `container`
                error =  f"La classe {subclass.__name__} ne peut pas avoir que deux paramètres dans son constructeur (self, container: str)."
                error += f"container correspond à où l'écriture va se faire (nom de fichier, nom de la base de donnée, ect)"
                raise TypeError(error)
            lower = name.lower()
            cls.__registry[lower] = subclass
            return subclass
        return decorator

    @classmethod
    def create_writter(cls, name: str, container: str) -> 'AWritter':
        """
        Instancie une classe writter à partir de son nom enregistré.
        """
        lower = name.lower()
        if lower not in cls.__registry:
            error = f"Writter: '{lower}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_writter('{lower}') en décoration de la classe dérivée pour enregistré le format."
            raise ValueError(error)
        return cls.__registry[name](container.lower())

    @classmethod
    def get_available_writter(cls) -> List[str]:
        """
        Retourne tous les writters disponibles.
        """
        return list(cls.__registry.keys())


    @classmethod
    def discover_writters(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les writters (ex. 'utils.writter').
        """
        dynamic_discovering(package=package, filename=__file__)