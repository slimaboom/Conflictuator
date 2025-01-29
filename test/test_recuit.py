import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.simulation import SimulationModel
from algorithm.data import SimulatedAircraftImplemented
from algorithm.concrete.recuit.recuit import AlgorithmRecuit
from algorithm.objective_function.function import ObjectiveFunctionMaxConflict
import time

def main():
    simulation = SimulationModel()
    aircrafts  = simulation.get_aircrafts()

    data = [SimulatedAircraftImplemented(aircraft) for aircraft in aircrafts.values()]

    # Critere est le nombre de conflits par avion: Maximisation
    recuit = AlgorithmRecuit(data=data, is_minimise=False, verbose=True)
    # Critere
    function = ObjectiveFunctionMaxConflict()
    # Envoie de la fonction objective dans l'algorithme
    recuit.set_objective_function(function)

    # Simulation
    simulation.start_simulation()
    time.sleep(1)
    simulation.stop_simulation()
    print(simulation.get_time_elapsed())

    # Recherche solution
    optimal_solution = recuit.start()
    print(optimal_solution)

if __name__ == "__main__":
    main()
