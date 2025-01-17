import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.simulation import SimulationModel
from algorithm.recuit.data import SimulatedAircraftImplemented
from algorithm.recuit.recuit import Recuit

import time

def main():
    simulation = SimulationModel()
    aircrafts  = simulation.get_aircrafts()

    data = [SimulatedAircraftImplemented(aircraft) for aircraft in aircrafts.values()]

    # Critere est le nombre de conflits par avion: Maximisation
    recuit = Recuit(data=data, is_minimise=False) 
    simulation.start_simulation()
    time.sleep(1)
    simulation.stop_simulation()
    print(simulation.get_time_elapsed())
    optimal_solution = recuit.run()
    print(optimal_solution)

if __name__ == "__main__":
    main()
