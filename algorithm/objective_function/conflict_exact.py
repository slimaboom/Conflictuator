from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft

from typing import List
from typing_extensions import override
import numpy as np
#-------------------------------------------------#
# Implementation de l'interface des fonctions objectives
""" cette fonction objective calcule la difference en nombre de conflit
entre le nombre de conflits reels et esperé en valeur absolue
il n'y aura donc pas de preference entre plus ou moins de conflits qu'esperé  """
    
# Evaluation par le nombre de conflit
class ObjectiveFunctionConflict(AObjective):


    nb_expected_conflict: int = 2

    def set_nb_expected_conflict(self, n: int) -> None:
        self.nb_expected_conflict = n
    
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
        total = np.abs(self.nb_expected_conflict - (total_conflicts * 0.5))
        return total
    
    @override
    def name(self) -> str:
        return f"{self.__class__.__name__}"
    