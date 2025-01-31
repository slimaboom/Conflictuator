from abc import abstractmethod
from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
from utils.controller.database_dynamique import MetaDynamiqueDatabase
from typing import Type
from typing_extensions import override

@ATrafficGenerator.register_traffic_generator
class ATrafficGeneratorDynamic(ATrafficGenerator):
    """Générateur abstrait dynamique de trafic aérien nécessitant un paramètre obligatoire (simulation_duration)."""
    
    @abstractmethod
    def __init__(self, simulation_duration: float, **kwargs):
        """
        Constructeur abstrait imposant un paramètre obligatoire.

        :param simulation_duration: Durée de simulation.
        :param kwargs: Hyperparamètres supplémentaires optionnels.
        """
        if simulation_duration <= 0:
            error = "simulation_duration doit être un entier positif."
            raise ValueError(error)

        super().__init__(**kwargs)  # Transmet les hyperparamètres à la classe parent
        self.__simulation_duration = simulation_duration
    
    @override
    def get_simulation_duration(self) -> float:
        """Renvoie la durée de la simulation"""
        return self.__simulation_duration
    
    @classmethod
    def register_traffic_generator(cls, traffic_class: Type):
        """
        Enregistre un generateur de traffic à partir de la classe ATrafficGeneratorDynamic.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.register(subclass=traffic_class)