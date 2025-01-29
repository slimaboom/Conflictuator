from abc import ABC, abstractmethod
from algorithm.interface.ISimulatedObject import ISimulatedObject, ASimulatedAircraft
from utils.controller.dynamic_discover_packages import dynamic_discovering
from utils.controller.database_dynamique import MetaDynamiqueDatabase

from typing import List
from typing_extensions import Type, override

import inspect

# Interface 
class IObjective(ABC):
    """Interface pour le calcul d'une fonction objectif a partir d'une liste de ISimulatedObject"""
    
    @abstractmethod
    def evaluate(self, data: List[ISimulatedObject]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Nom pour decrire la fonction Objectif"""
        pass

# Abstraction
class AObjective(IObjective):
    """Classe abstraite pour le calcul d'une fonction objectif a partir d'une liste de ASimulatedAircraft"""

    @abstractmethod
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        """Calcule la fonction objectif a partir de data (generique)."""
        pass

    @override
    def name(self) -> str:
        return f"{self.__class__.__name__}"


    @classmethod
    def register_objective_function(cls, objectif_class: Type):
        """
        Enregistre une fonction objective à partir de la classe.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.register(objectif_class)

    @classmethod
    def get_available_objective_functions(cls):
        """
        Retourne la liste des noms des fonctions objectives disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)


    @classmethod
    def discover_objective_functions(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné ('algorithm.objective_function')
        
        :param package: Le chemin du package où chercher les fonctions objectives (ex. 'algorithm.objective_function').
        """
        dynamic_discovering(package=package)
    
    @classmethod
    def get_objective_class(cls, name: str) -> 'AObjective':
        """
        Renvoie une classe AObjective à partir de son nom enregistré.
        L'instance n'est pas crée.
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"Objectif '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_objective_function('{name}') en décoration de la classe dérivée pour enregistré la fonction objectif."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)
    
    @classmethod
    def create_objective_function(cls, name: str, *args, **kwargs) -> 'AObjective':
        """
        Instancie une classe AObjective à partir de son nom enregistré.
        Exception: TypeError ou ValueError
        """
        return cls.get_objective_class(name)(*args, **kwargs)

    @classmethod
    def get_class_constructor_params(cls, class_name: str):
        """
        Retourne les paramètres du constructeur de la fonction objectif spécifiée.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_class_constructor_params(cls, class_name)