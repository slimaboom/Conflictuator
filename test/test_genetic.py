import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.simulation import SimulationModel
from algorithm.data import SimulatedAircraftImplemented
from algorithm.genetic.genetique import AlgorithmGenetic
from algorithm.objective_function.conflict_objective import ObjectiveFunctionMaxConflict
import time

def main():
    simulation = SimulationModel()
    aircrafts  = simulation.get_aircrafts()

    data = [SimulatedAircraftImplemented(aircraft) for aircraft in aircrafts.values()]

    # Critere est le nombre de conflits par avion: Maximisation
    genetic = AlgorithmGenetic(data=data, is_minimise=False, verbose=True)
    # Critere
    function = ObjectiveFunctionMaxConflict()
    # Envoie de la fonction objective dans l'algorithme
    genetic.set_objective_function(function)

    # Simulation
    simulation.start_simulation()
    time.sleep(1)
    simulation.stop_simulation()
    print(simulation.get_time_elapsed())

    # Recherche solution
    for _ in range(1):
        optimal_solution = genetic.start()
        for i, sol in enumerate(optimal_solution):
            data[i].update_commands(sol)
            print(f"Maj commande {data[i]}")
        
        time.sleep(5)
        print(optimal_solution)

if __name__ == "__main__":
    main()
