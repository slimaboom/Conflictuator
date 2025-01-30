from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft

from typing import List
from typing_extensions import override

@AObjective.register_objective_function
class ObjectiveFunctionAbsoluteNumberConflict(AObjective):
    """
    Cette classe implémente une fonction objective qui calcule la différence absolue
    entre le nombre de conflits réels et le nombre de conflits attendus. 
    Cette fonction n'applique aucune préférence entre avoir plus ou moins de conflits
    que celui attendu.

    Cette fonction objective est souvent utilisée pour minimiser la différence entre
    un résultat attendu (nombre de conflits) et le résultat obtenu par un algorithme,
    en optimisant les solutions pour avoir un nombre de conflits aussi proche que possible
    du nombre attendu.

    Attributes:
        number_of_conflict_expected (int): Le nombre de conflits attendu (par défaut 2).

    Methods:
        __init__(self, number_of_conflict_expected: int = 2):
            Initialise la fonction objective avec un nombre de conflits attendu.
        
        evaluate(self, real_conflicts: int) -> int:
            Calcule et retourne la différence absolue entre le nombre de conflits réels
            et le nombre de conflits attendus.
    """
    def __init__(self, nunber_of_conflict_expected: int = 2):
        """
        Initialise la fonction objective avec un nombre de conflits attendu.

        :param number_of_conflict_expected: int, nombre de conflits attendus (par défaut 2)
        """
        super().__init__()
        self.__nb_expected_conflict = nunber_of_conflict_expected

    @override
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        total_conflicts = 0
        nc = 0.
        conflict = []
        for _, aircraft_sim in enumerate(data):
            for conflicts in aircraft_sim.get_object().get_conflicts().get_all().values():
                if conflicts not in conflict:
                    conflict.append(conflicts)
                    nc = len(conflicts)
                    total_conflicts += nc
        #print("c'est la ", self.nb_conflicts, total_conflicts)
        total = abs(self.__nb_expected_conflict - (total_conflicts * 0.5))
        return total
    
    @override
    def name(self) -> str:
        return f"{self.__class__.__name__}"