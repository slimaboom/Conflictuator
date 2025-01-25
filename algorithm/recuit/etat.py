from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from algorithm.storage import DataStorage

from logging_config import setup_logging

from typing import List, Callable
from copy import deepcopy

import numpy as np

class Etat:
    """
        Etat d'un recuit simulé
    """

    generator = np.random.Generator(bit_generator=np.random.PCG64(seed=123))

    def __init__(self, data: List[ASimulatedAircraft]):
        if not all(isinstance(item, ASimulatedAircraft) for item in data):
            msg = f"L'objet data doit être une liste d'objets implémentant ASimulatedAircraft"
            raise TypeError(msg)

        self.logger = setup_logging(__class__.__name__)

        self.dimension: int = len(data)
        self.data           = data
        # Vector est un vecteur de donnees stockant les valeurs (pas de modification)
        self.vector: List[DataStorage]    = []
        self.critere = None

    def initialize_random(self) -> None:
        """Generation d'un etat aleatoire"""
        # Debug : le 25/01/2025 11:16:00
        # Le vecteur d'etat:
        #       - n'est pas encore initialiser, appeler:  obj.initialize()
        #       - est deja initialiser, generer un voisin: obj.obj.generate_neighbor()
        
        if len(self.vector) <= 0: 
            for obj in self.data:
                obj.update_commands(commands=obj.initialize())
                self.vector.append(obj.get_data_storages())
        else:
            for i, obj in enumerate(self.data):
                # Initialisation des objets par une selection d'un voisin pour chaque objet
                obj.generate_neighbor() # modification en place des commandes dans obj
                # la mise a jour des commandes est faite dans generate_neighbor
                self.vector[i] = obj.get_data_storages()

    def generate_neighborhood(self):
        """Générer un état voisin."""

        # Selection aleatoire d'un element du vecteur (un ISimulatedObject)
        i = self.generator.integers(low=0, high=self.dimension) # [0, dim - 1]

        # Generation d'un voisin de cet objet
        obji = self.data[i]
        obji.generate_neighbor()

        self.vector[i] = obji.get_data_storages()
        self.data[i] = obji
        
    def calcul_critere(self, function: Callable) -> float:
        """Evaluation du critere (fonction objectif) prenant une List[ASimulatedAircraft]"""
        if isinstance(function, Callable):
            self.critere = function(self.data)
            return self.critere

        msg = f"function argument must be Callable with on parameter of type List[ASimulatedAircraft]"
        raise TypeError(msg) 
    
    def copy(self, copy_from: 'Etat') -> None:
        self.vector    = copy_from.vector[:]
        self.data      = copy_from.data[:]
        self.dimension = copy_from.dimension
        self.critere   = copy_from.critere

    def save_state(self, other: 'Etat') -> None:
        self.vector    = [deepcopy(v) for v in other.vector]
        self.data      = other.data[:]
        self.dimension = other.dimension
        self.critere   = other.critere

    def restore_state(self, other: 'Etat') -> None:
        self.dimension = other.dimension

        for i in range(self.dimension):
            ovi = other.vector[i]
            obji = other.data[i]
            obji.update_commands(commands=ovi)

            self.vector[i] = ovi
            self.data[i] = obji

    def display(self) -> str:
        """Affichage de l'Etat"""
        msg = f"Critere: {self.critere}"
        msg += f"\n{self.vector}\n"
        return msg
    
    def get_vector(self) -> List[List[DataStorage]]:
        return self.vector
    
    def __repr__(self):
        return self.display()