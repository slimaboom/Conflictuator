from typing import List
from algorithm.recuit.data import ISimulatedObject
from algorithm.objective_function.IObjective import IObjective

#-------------------------------------------------#
# Implementation de l'interface 
    
# Evaluation par le nombre de conflit    
class ConflictEvaluationStrategy(IObjective):
    def evaluate(self, data: List[ISimulatedObject]) -> float:
        total_conflicts = 0
        for _, aircraft_sim in enumerate(data):
          #  trajectory = self.individual[i]
          #  aircraft = aircraft_sim.aircraft
          #  aircraft.set_take_off_time(trajectory[0].time)
          #  aircraft.set_speed(trajectory[0].speed)
          #  aircraft.set_commands(trajectory)
            total_conflicts += aircraft_sim.evaluate()
        return total_conflicts
    
