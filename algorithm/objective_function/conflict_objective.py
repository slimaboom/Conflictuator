from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft

from typing import List
from typing_extensions import override
#-------------------------------------------------#
# Implementation de l'interface des fonctions objectives
    
# Evaluation par le nombre de conflit
class ObjectiveFunctionMaxConflict(AObjective):
    
    @override
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        total_conflicts = 0
        nc = 0.
        for _, aircraft_sim in enumerate(data):
            for conflicts in aircraft_sim.get_object().get_conflicts().get_all().values():
                nc = len(conflicts)
                total_conflicts += nc
        return (total_conflicts * 0.5)
    
    @override
    def name(self) -> str:
        return f"{self.__class__.__name__}"
    