import numpy as np
import random
from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.genetic.genetique import AlgorithmGenetic
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from algorithm.storage import DataStorage
from logging_config import setup_logging
from utils.controller.argument import method_control_type
from algorithm.objective_function.function import ObjectiveFunctionConflict

from typing import List, Dict, Tuple
from typing_extensions import override
from copy import deepcopy
from time import time
from collections import defaultdict

#@AAlgorithm.register_algorithm
class OptimizedGeneticAlgorithm(AAlgorithm):
    def __init__(self, data: List[ASimulatedAircraft],
                 is_minimise: bool = True,
                 verbose: bool = False,
                 timeout: float = 120,
                 population_size: int = 10,
                 generations: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 early_stopping: int = 10,
                 interval_value: int = 5,
                 time_window: int = 1200):
        
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, timeout=timeout)
        
        self.__population_size = population_size
        self.__generations  = generations
        self.__mutation_rate  = mutation_rate
        self.__crossover_rate  = crossover_rate
        self.__time_window  = time_window
        
        self.early_stopping = early_stopping
        self.interval_type: str = "time" # or'group'
        self.best_solutions: List[List[DataStorage]] = []
        self.aircraft_intervals: Dict[int, List[List[DataStorage]]] = defaultdict(list)
        self.optimal_individual = []


    def __generate_individuals(self, data: List[ASimulatedAircraft]) -> List[List[DataStorage]]:
        """Generation d'un individu (commandes) pour chaque ASimulatedAircraft"""
        # on sépare les individus par intervalle
        intervals = self.split_intervals()
        # on initialise et on remplit la liste des solutions completes
        all_solutions: List[Tuple[List[List[DataStorage]], float]] = []
        for interval in intervals:
            best_solution, fitness = self.run_genetic_on_interval(interval)
            all_solutions.append((best_solution, fitness))

        # Fusion des solutions
        merged_solution = self.merge_solutions(all_solutions)

        return merged_solution

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
    
    def __calculate_fitnesses(self, population: List[List[List[DataStorage]]], recalcul=True) -> List[float]:
        """Calcul les differentes fitnesses pour chaque individu de la population"""
        fitnesses = []
        data_copy = deepcopy(self.get_data())
        for individual in population:
            print(len(individual), len(self.get_data()))
            for i, aircraft_sim in enumerate(self.get_data()):
                trajectory = individual[i]
                aircraft_sim.update_commands(trajectory, recalcul=recalcul)

        # A calculer apres avoir changer chaque avion 
        fitnesses.append(self.evaluate(data_copy)) # Evaluation du critere avec la List[ASimulatedAircraft]
        return fitnesses
    
    def __next_population(self, population: List[List[List[DataStorage]]], fitnesses: List[float], iterations: int = 40, n: int = 5, dt_range: Tuple[int, int] = (-300, 300)) -> List[List[List[DataStorage]]]:
        """Calcul la prochaine population en fonction de la precedante et des valeurs de fitnesses"""
        next_population = []
        for i in range(self.population_size):
            
            # Sélectionner `n` indices d'avions et les trier par ordre croissant
            selected_indices = sorted(np.random.choice(len(self.get_data()), size=n, replace=False))
            dt = np.random.randint(*dt_range)
            new_individual = []
            for idx, aircraft_sim in enumerate(self.get_data()):
            # Modifier les commandes des avions sélectionnés
                if idx in selected_indices:
                    #trier new solution par id
                    if len(population) != self.population_size :
                        aircraft_commands = population[0][idx]
                    else:
                        print(i, len(population), idx, len(population[i % len(population)]))
                        aircraft_commands = population[i % len(population)][idx]  # Liste de commandes (DataStorage)

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
                    new_solution.append(new_traj)
                else: 
                    new_solution.append(aircraft_sim.get_object().get_commands())
            next_population.append(new_solution)
        return next_population
    
    @override
    def run(self) -> List[List[DataStorage]]:

        if self.is_verbose():
            self.logger.info(f"Il y a {len(self.get_data())} ASimulatedAircraft")

        self.set_process(0.)
        self.set_start_time(start=time())

        population      = [self.__generate_individuals(self.get_data())]
        best_individual = population[0]
        best_fitness    = self.__calculate_fitnesses(population=population)[0]

        for generation in range(self.generations):
            print(generation)
            if not self.is_running():
                break  

            # Calcul fitnesses
            fitnesses = self.__calculate_fitnesses(population, recalcul=False)
            #self.logger.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            # Acceptation ou non du critere
            if self.is_minimisation():
                optimal_fitness = min(fitnesses)
                if (generation <= 0) or (optimal_fitness < best_fitness) or (best_fitness == None):
                    best_fitness   = deepcopy(optimal_fitness)
                    best_individual = deepcopy(population[fitnesses.index(optimal_fitness)])
                    self.best_results = [best_individual]
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])
            else: # Maximisation
                optimal_fitness = max(fitnesses)
                if (generation <= 0) or (optimal_fitness > best_fitness) or (best_fitness == None):
                    best_fitness   = deepcopy(optimal_fitness)
                    best_individual = deepcopy(population[fitnesses.index(optimal_fitness)])
                    self.best_results = [best_individual]
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])

            # Logger
            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Best Individual = {best_individual}")

            # Calcul de la Prochaine population
            population = self.__next_population(population, fitnesses)

            # Avancement du processus
            self.set_process(int(((generation + 1) / self.generations) * 100))
            self.set_process_time(process_time=time() - self.get_start_time())

            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Progress = {self.get_progress()}%")

        self.stop()
        self.logger.info(f"Final Best Solution(fitness: {best_fitness}): {best_individual}")
        self.reinitialize_data()
        return best_individual