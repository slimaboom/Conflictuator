from algorithm.recuit.data import ISimulatedObject
import numpy as np
from typing import List
from logging_config import setup_logging

class Etat:
    """
        Etat d'un recuit simulé
    """

    generator = np.random.Generator(bit_generator=np.random.PCG64(seed=123))

    def __init__(self, data: List[ISimulatedObject]):
        if not all(isinstance(item, ISimulatedObject) for item in data):
            msg = f"L'objet data doit être une liste d'objets implémentant ISimulatedObject"
            raise TypeError(msg)

        self.logger = setup_logging(__class__.__name__)

        self.dimension = len(data)
        self.data      = data
        # Vector est un vecteur de donnees stockant les valeurs (pas de modification)
        self.vector    = []

    def initialize_random(self) -> None:
        """Generation d'un etat aleatoire"""
        for obj in self.data:
            # Initialisation des objets par une selection d'un voisin initiale pour chaque objet
            self.vector.append(obj.get_data_storage())

    def generate_neighborhood(self):
        """Générer un état voisin."""

        # Selection aleatoire d'un element du vecteur (un ISimulatedObject)
        i = self.generator.integers(low=0, high=self.dimension) # [0, dim - 1]

        # Generation d'un voisin de cet objet
        obji = self.data[i]
        obji.generate_neighbor()

        self.vector[i] = obji.get_data_storage()
        self.data[i] = obji
        
    def calcul_critere(self) -> float:
        """Evaluation du critere (fonction objectif)"""
        critere = 0.
        for obj in self.data:
            critere += obj.evaluate()
        return critere
    
    def copy(self, copy_from: 'Etat') -> None:
        self.vector    = copy_from.vector[:]
        self.data      = copy_from.data[:]
        self.dimension = copy_from.dimension

    def save_state(self, other: 'Etat') -> None:
        self.copy(copy_from=other)

    def restore_state(self, other: 'Etat') -> None:
        self.dimension = other.dimension

        for i in range(self.dimension):
            ovi = other.vector[i]
            obji = other.data[i]
            obji.update(value=ovi.speed)

            self.vector[i] = ovi
            self.data[i] = obji

    def display(self) -> str:
        """Affichage de l'Etat"""
        msg = f"Critere: {self.calcul_critere()}"
        msg += f"\n{self.vector}\n"
        return msg
    
    def __repr__(self):
        return self.display()