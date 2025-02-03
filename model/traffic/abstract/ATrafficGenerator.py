from abc import abstractmethod
from model.traffic.interface.ITrafficGenerator import ITrafficGenerator
from utils.controller.database_dynamique import MetaDynamiqueDatabase
from typing import Type, Any

class ATrafficGenerator(ITrafficGenerator):
    """Classe abstraite contenant des méthodes utilitaires communes."""
    
    @abstractmethod
    def __init__(self, **kwargs):
        """
        Initialise la classe et stocke des paramètres supplémentaires via kwargs.
        """
        self.extra_params = kwargs  # Stocker les hyperparamètres additionnels

    def get_param(self, param_name: str, default=None) -> Any:
        """Retourne un paramètre stocké ou la valeur par défaut"""
        return self.extra_params.get(param_name, default)
    

    @classmethod
    def register_traffic_generator(cls, traffic_class: Type):
        """
        Enregistre un generateur de traffic à partir de la classe.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.register(subclass=traffic_class)

    @classmethod
    def get_available_traffic_generators(cls):
        """
        Retourne la liste des noms des traffic generator disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)

    @classmethod
    def discover_traffic_generators(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné ('model.traffic')
        
        :param package: Le chemin du package où chercher les traffic generators (ex. 'model.traffic').
        """
        return MetaDynamiqueDatabase.discover_dynamic(package=package)
    
    @classmethod
    def get_traffic_generator_class(cls, name: str) -> 'ATrafficGenerator':
        """
        Renvoie une classe ATrafficGenerator à partir de son nom enregistré.
        L'instance n'est pas crée.
        Exception: TypeError ou ValueError
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"TrafficGenerator '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_traffic_generator en décoration de la classe dérivée pour enregistrer le traffic generator."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)
    
    @classmethod
    def create_traffic_generator(cls, name: str, *args, **kwargs) -> 'ATrafficGenerator':
        """
        Instancie une classe ATrafficGenerator à partir de son nom enregistré.
        Exception: TypeError ou ValueError
        """
        return cls.get_traffic_generator_class(name)(*args, **kwargs)


    @classmethod
    def get_class_constructor_params(cls, class_name: str):
        """
        Retourne les paramètres du constructeur du traffic generator spécifiée.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_class_constructor_params(cls, class_name)
       

