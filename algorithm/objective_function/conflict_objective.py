from abc import ABC
from typing import List
from algorithm.recuit.data import ISimulatedObject
from algorithm.storage import DataStorage
from objective_function.IObjective import IObjective, ObjectiveError

#-------------------------------------------------#
# Implementation de l'interface 
    
# Evaluation par le nombre de conflit    
class ConflictEvaluationStrategy(IObjective):
    def __init__(self):
        self.individual = None
    
    def set_individual(self, individu: List[List[DataStorage]]) -> None:
        self.individual = individu

    def evaluate(self, data: List[ISimulatedObject]) -> float:
        if self.individual == None:
            msg = f"{self.__class__.__name__} attribute individual not set, please use set_individual method before using evaluate method"
            raise ObjectiveError(msg)
        
        total_conflicts = 0
        for i, aircraft_sim in enumerate(data):
            trajectory = self.individual[i]
            aircraft = aircraft_sim.aircraft
            aircraft.set_take_off_time(trajectory[0].time)
            aircraft.set_speed(trajectory[0].speed)
            aircraft.set_commands(trajectory)
            total_conflicts += aircraft_sim.evaluate()
        return total_conflicts
    
