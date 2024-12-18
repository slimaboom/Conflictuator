from enum import Enum

class AlgoType(Enum):
    NO_ALGO: str = "No Algorithm"
    RECUIT: str = "Simulated Annealing"
    GENETIQUE: str = "Genetic"

    @staticmethod
    def find(value: str) -> 'AlgoType':
        # Parcours de l'énumération pour trouver le type correspondant à la valeur
        for algo in AlgoType:
            if algo.value == value:
                return algo
        return None  # Retourner None si aucun élément ne correspond