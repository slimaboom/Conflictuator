from abc import abstractmethod
from datetime import time
from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
from utils.controller.database_dynamique import MetaDynamiqueDatabase
from utils.conversion import time_to_sec
from typing_extensions import override

@ATrafficGenerator.register_traffic_generator
class ATrafficGeneratorDynamic(ATrafficGenerator):
    """Générateur abstrait dynamique de trafic aérien nécessitant un paramètre obligatoire (simulation_duration)."""
    
    @abstractmethod
    def __init__(self, simulation_duration: time, **kwargs):
        """
        Constructeur abstrait imposant un paramètre obligatoire.

        :param simulation_duration: Durée maximale de la simulation (en objet datetime.time).
        :param kwargs: Hyperparamètres supplémentaires optionnels.
        """
        duration = time_to_sec(simulation_duration.isoformat())
        if duration <= 0:
            error = "simulation_duration objet datetime.time) avec un contenu positif pour heure, minute, secondes."
            raise ValueError(error)

        super().__init__(**kwargs)  # Transmet les hyperparamètres à la classe parent
        self.simulation_duration = duration
    
    @override
    def get_simulation_duration(self) -> float:
        """Renvoie la durée de la simulation en secondes"""
        return self.simulation_duration
    
    def set_simulation_duration(self, simulation_time: float) -> None:
        """Set la valeur de simulation pour pouvoir l'ajuster depuis des classes dérivées
        Modification de l'attribut par : max(attribut, simulation_time)"""
        # N'écraser la valeur que si elle est plus grande pour protéger la plus grande durée
        # La méthode est utilisé dans les classes dérivées pour prendre
        # le dernier temps de passages du dernier avions et envoyés la valeur dans l'attribut
        self.simulation_duration = max(self.simulation_duration, simulation_time) 

    
    @classmethod
    @override # redefinit le comportement de la classe parent pour cette classmethod
    def get_class_constructor_params(cls, class_name: str):
        """
        Retourne les paramètres du constructeur du traffic generator spécifiée.
        Le paramètre simulation_duration du constructeur de la classe ATrafficGeneratorDynamic
        doit être convertie pour l'affichage coté IHM
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_class_constructor_params(cls, class_name)