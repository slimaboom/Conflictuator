import numpy as np
import random
from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.genetic.genetique import AlgorithmGenetic
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from model.aircraft.storage import DataStorage

from utils.conversion import time_to_sec

from typing import List, Dict, Tuple
from typing_extensions import override
from copy import deepcopy
from datetime import time, datetime
from collections import defaultdict

#@AAlgorithm.register_algorithm
class OptimizedGeneticAlgorithm(AAlgorithm):
    def __init__(self, data: List['ASimulatedAircraft'],
                 is_minimise: bool,
                 verbose: bool = False,
                 population_size: int = 10,
                 generations: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 early_stopping: int = 10,
                 interval_type: str = "time",  # "time" or "group"
                 interval_value: int = 5,  # Minutes or number of aircraft
                 t: time = time(hour=0, minute=20, second=0), 
                 **kwargs):
        
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, **kwargs)
        
        self.population_size: int = population_size
        self.generations: int = generations
        self.mutation_rate: float = mutation_rate
        self.crossover_rate: float = crossover_rate
        self.early_stopping: int = early_stopping
        self.interval_type: str = interval_type
        self.__t: int = time_to_sec(t.isoformat())
        
        self.best_solutions: List[List[DataStorage]] = []
        self.aircraft_intervals: Dict[int, List[List[DataStorage]]] = defaultdict(list)
        self.optimal_individual = []

    @override
    def run(self) -> List[List[DataStorage]]:
        """ Exécute l'algorithme génétique optimisé par intervalles """
        # on sépare les individus par intervalle
        intervals = self.split_intervals()
        # on initialise et on remplit la liste des solutions completes
        all_solutions: List[Tuple[List[List[DataStorage]], float]] = []
        for interval in intervals:
            best_solution, fitness = self.run_genetic_on_interval(interval)
            all_solutions.append((best_solution, fitness))

        # Fusion des solutions
        merged_solution = self.merge_solutions(all_solutions)
        
        # Appliquer un génétique allégé sur l'ensemble
        final_solution = self.refine_with_light_genetic(merged_solution)
        
        return final_solution

    def split_intervals(self) -> List[List[List[DataStorage]]]:
        """ Divise les données en intervalles temporels ou par groupes d'avions """
        if self.interval_type == "time":
            return self.split_by_time()
        elif self.interval_type == "group":
            return self.split_by_group()
        else:
            raise ValueError("interval_type must be 'time' or 'group'")
    
    def split_by_time(self) -> List[List[List[DataStorage]]]:
        """ Divise les avions en fonction de leur temps de départ """
        num_intervals = int(3600 // self.__t)
        
        for obj in self.get_data():
            take_off_time = obj.get_object().get_commands()[0].time 
            interval_index = int(take_off_time // self.__t)
            
            if interval_index < num_intervals:
                #on remplit avec une deepcopy des avions
                self.aircraft_intervals[interval_index].append(deepcopy(obj))
        
        return list(self.aircraft_intervals.values())
    
    def split_by_group(self) -> List[List[List[DataStorage]]]:
        """ Divise les avions en groupes de taille fixe """
        return [self.data[i:i+self.interval_value] for i in range(0, len(self.data), self.interval_value)]
    
    def run_genetic_on_interval(self, interval_data: List[List[DataStorage]]) -> Tuple[List[List[DataStorage]], float]:
        """ Applique un algorithme génétique sur un intervalle donné et retourne la meilleure solution """
        
        algo = AlgorithmGenetic(
            data=deepcopy(interval_data), 
            generations=self.generations,
            population_size=self.population_size,
            is_minimise=True, 
            verbose=False, 
            early_stopping=self.early_stopping,
        )

        algo.set_objective_function(self.get_objective_function())
        best_solution, fitness = deepcopy(algo.startbis())
        
        
        return best_solution, fitness
    
    def merge_solutions(self, solutions: List[Tuple[List[List[DataStorage]], float]]) -> List[List[DataStorage]]:
        """ Fusionne les meilleures solutions des intervalles pour former une solution complète """
        merged_solution: List[List[DataStorage]] = []
        for best_solution, _ in solutions:
            merged_solution.extend(best_solution)
        
        return merged_solution
    
    def refine_with_light_genetic(self, merged_solution: List[List[DataStorage]], iterations: int = 40, n: int = 5, dt_range: Tuple[int, int] = (-300, 300)) -> List[List[DataStorage]]:
        """ Applique une optimisation légère sur un nombre restreint d'avions """
        best_solution = merged_solution
        best_solution = [sorted(commands, key=lambda cmd: cmd.id) for commands in best_solution]
        for i, aircraft_sim in enumerate(self.get_data()):
            for j in range(len(best_solution)):
                # on verieife si l'id de l'aircraft correspond à l'id de la solution
                if aircraft_sim.get_object().id == best_solution[j][0].id:
                    trajectory = best_solution[j]
                    # on modifie data directement
                    aircraft_sim.update_commands(trajectory)
        best_fitness = self.evaluate(self.get_data())

        for itera in range(iterations):
            print(itera)
            
            if len(best_solution) < n:
                n = len(best_solution)

            # Sélectionner `n` indices d'avions et les trier par ordre croissant
            selected_indices = sorted(np.random.choice(len(best_solution), size=n, replace=False))
            dt = np.random.randint(*dt_range)
            print(dt)

            # Modifier les commandes des avions sélectionnés
            for idx in selected_indices:
                new_solution = []
                #trier new solution par id
                aircraft_commands = best_solution[idx]  # Liste de commandes (DataStorage)
                new_traj = []
                # Modifier la première commande (temps de départ)
                for commands in aircraft_commands:  # Vérifier que l'avion a des commandes
                    old_command = commands
                    new_command = DataStorage(
                    speed=old_command.speed,
                    id=old_command.id,
                    time=old_command.time + dt,  # Modifier le temps
                    heading=old_command.heading
                )
                    commands = new_command
                    new_traj.append(commands)
                    for i, aircraft_sim in enumerate(self.get_data()):
                        if aircraft_sim.get_object().id == idx :
                            aircraft_sim.update_commands(new_traj, recalcul=False, dt=dt)
                        #for c in aircraft_sim.get_object().get_conflicts().get_all().values() :
                            #print(c)
                new_solution.append(new_traj)
            new_fitness = self.evaluate(self.get_data())
            print(new_fitness)
            
            # Si meilleur fitness modifie
            if new_fitness < best_fitness:
                best_solution = new_solution
                best_fitness = new_fitness

            # Si l'individus a une fitness optimal on l'ajoute à la liste pour le early stopping
            elif new_fitness == best_fitness :
                self.optimal_individual.append(best_solution)
            
            # Choix d'une des meilleurs solution
            selected_indices = random.randint(0, len(self.optimal_individual)-1)
            best_solution = self.optimal_individual[selected_indices]
            print(best_fitness)
            
            #early stopping
            if len(self.optimal_individual) > 20:
                break


        return best_solution


