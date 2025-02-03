import numpy as np
import random
from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.genetic.genetique import AlgorithmGenetic
from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from algorithm.objective_function.exact import ObjectiveFunctionAbsoluteNumberConflict
from algorithm.objective_function.function import ObjectiveFunctionMaxConflict, ObjectiveFunctionTimeStdDev
from model.aircraft.storage import DataStorage
from logging_config import setup_logging
from utils.controller.argument import method_control_type

from typing import List, Dict, Tuple
from typing_extensions import override
from copy import deepcopy
from time import time
from collections import defaultdict

@AAlgorithm.register_algorithm

class OptimizedGeneticAlgorithm(AAlgorithm):
    
    def __init__(self, 
                 data: List['ASimulatedAircraft'],
                 is_minimise: bool = True,
                 verbose: bool = False,
                 timeout: float = 120,
                 population_size: int = 10,
                 generations: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 early_stopping: int = 10,
                 interval_value: int = 5,
                 time_window: int = 1200,

    ):
        
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, timeout=timeout)
        
        self.__population_size = population_size
        self.__generations  = generations
        self.__mutation_rate  = mutation_rate
        self.__crossover_rate  = crossover_rate
        self.__time_window  = time_window
        
        self.early_stopping = early_stopping
        self.interval_type: str = "group" # or'time'
        self.best_solutions: List[List[DataStorage]] = []
        self.aircraft_intervals: Dict[int, List['ASimulatedAircraft']] = defaultdict(list)
        self.optimal_individual = []
        self.interval_value = interval_value
        self.num_layers: int = 2
        self.evaluation_functions: List[AObjective] = [ObjectiveFunctionTimeStdDev(), ObjectiveFunctionAbsoluteNumberConflict(3)]
        self.layer_population_size: List[int] = [10, 10]
        self.layer_generations: List[int] = [10, 10]


    def split_intervals(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les données en intervalles temporels ou par groupes d'avions """
        if self.interval_type == "time":
            return self.split_by_time()
        elif self.interval_type == "group":
            return self.split_by_group()
        else:
            raise ValueError("interval_type must be 'time' or 'group'")
    
    def split_by_time(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les avions en fonction de leur temps de départ """
        num_intervals = int(3600 // self.__time_window)
        
        for obj in self.get_data():
            take_off_time = obj.get_object().get_commands()[0].time 
            interval_index = int(take_off_time // self.__time_window)
            
            if interval_index < num_intervals:
                #on remplit avec une deepcopy des avions
                self.aircraft_intervals[interval_index].append(deepcopy(obj))
        
        return self.aircraft_intervals
    
    def split_by_group(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les avions en groupes de taille fixe et met le reste dans le dernier groupe """
        
        part = [self.get_data()[i:i+self.interval_value] for i in range(0, len(self.get_data()), self.interval_value)]
        self.aircraft_intervals = {i: [] for i in range(len(part))}
        for interval_index in range(len(part)):  # S'assure de ne pas dépasser la taille de `part`
            self.aircraft_intervals[interval_index] = part[interval_index]
        return self.aircraft_intervals
    
    def run_genetic_on_interval(self, interval_data: List['ASimulatedAircraft'], idx_layer: int, start_with_dataStorages: List[List[List[DataStorage]]] = None) -> Tuple[List[List[DataStorage]], float, List[List[List[DataStorage]]]]:
        """ Applique un algorithme génétique sur un intervalle donné et retourne la meilleure solution """
        print(start_with_dataStorages)
        algo: 'AAlgorithm' = AlgorithmGenetic(
            data=interval_data, 
            is_minimise=True, 
            verbose=True, 
            timeout= 120,
            generations=self.layer_generations[idx_layer],
            population_size=self.layer_population_size[idx_layer],
            mutation_rate = self.__mutation_rate,
            crossover_rate = self.__crossover_rate,
            early_stopping=self.early_stopping,
        )

        algo.set_objective_function(self.evaluation_functions[idx_layer])
        algo.set_initial_population(start_with_dataStorages)
        best_solution, fitness, bests = deepcopy(algo.startbis()) 
        
        return best_solution, fitness, bests
    
    def shuffle(self, solution: List[List[DataStorage]], simulation_end_time: int = 3600) -> List[List[DataStorage]]:
        """
        Décale aléatoirement les commandes dans le temps en s'assurant que
        - Aucun avion ne commence avant 0
        - Aucun avion ne dépasse la fin de la simulation (simulation_end_time)
        """
        best_delayed = []

        # Générer un décalage aléatoire
        dt: int = random.randint(-300, 300)

        # Trouver les temps de départ minimaux et maximaux
        min_time = min(min(cmd.time for cmd in aircraft) for aircraft in solution)
        max_time = max(max(cmd.time for cmd in aircraft) for aircraft in solution)

        # Ajustement de dt si nécessaire
        if min_time + dt < 0:
            dt = -min_time  # Ajuster pour que le premier avion commence à 0
        elif max_time + dt > simulation_end_time:
            dt = simulation_end_time - max_time  # Ajuster pour que le dernier avion termine à la limite

        # Appliquer le décalage corrigé à toutes les commandes
        for old_commands in solution:
            delayed_aircraft = []
            for old_command in old_commands:
                new_command = DataStorage(
                    id=old_command.id,
                    speed=old_command.speed,
                    time=old_command.time + dt  # Appliquer dt ajusté
                )
                delayed_aircraft.append(new_command)
            best_delayed.append(delayed_aircraft)

        return best_delayed

    
    def merge_solutions(self, solutions: Tuple[List[List[DataStorage]], float]) -> List[List[DataStorage]]:
        """ Fusionne les meilleures solutions des intervalles pour former une solution complète """
        merged_solution: List[List[List[DataStorage]]] = []
        for _ in range(self.__population_size) :
            merged__partial_solution: List[List[DataStorage]] = []
            for best, _ in solutions:
                n = random.randint(0, len(best))
                for _ in range(len(solutions)):
                    merged__partial_solution.extend(best[n])
            merged_solution.extend(merged__partial_solution)
        return merged_solution
    
    def __calculate_fitnesses(self, data : List['ASimulatedAircraft'], population: List[List[List[DataStorage]]], recalcul=True) -> List[float]:
        """Calcul les differentes fitnesses pour chaque individu de la population"""
        fitnesses = []
        data_copy = deepcopy(data)
        for individual in population: 
            for i, aircraft_sim in enumerate(data_copy):

                trajectory = individual[i]
                aircraft_sim.update_commands(trajectory, recalcul=recalcul)
        # A calculer apres avoir changer chaque avion 
        fitnesses.append(self.evaluate(data_copy)) # Evaluation du critere avec la List[ASimulatedAircraft]
        return fitnesses

    
    def partial_shuffle(self, solution: List[List[DataStorage]], dt: int, first_departure: float, last_departure: float) -> List[List[DataStorage]]:
        """
        Décale aléatoirement les temps des commandes de chaque avion dans la solution,
        en s'assurant que les temps restent dans l'intervalle [first_departure, last_departure].

        :param solution: Liste des trajectoires de la population (List[List[DataStorage]])
        :param dt: Valeur maximale de décalage (chaque commande est décalée entre -dt et +dt)
        :param first_departure: Temps minimum autorisé pour la première commande de chaque avion
        :param last_departure: Temps maximum autorisé pour la dernière commande de chaque avion
        :return: Une nouvelle version de la solution avec les commandes ajustées
        """
        shuffled_solution = []

        for old_commands in solution:
            delayed_aircraft = []

            # Générer un décalage aléatoire entre -dt et +dt
            delta_t = random.uniform(-dt, dt)

            for old_command in old_commands:
                new_time = old_command.time + delta_t

                # Assurer que le temps reste dans les bornes [first_departure, last_departure]
                new_time = max(first_departure, min(new_time, last_departure))

                new_command = DataStorage(
                    id=old_command.id,
                    speed=old_command.speed,
                    time=new_time
                )
                delayed_aircraft.append(new_command)

            shuffled_solution.append(delayed_aircraft)

        return shuffled_solution
    

    def select_all_best_individuals(self, interval_populations: Dict[int, List[List[List[DataStorage]]]]) -> Dict[int, List[List[List[DataStorage]]]]:
        """
        Récupère **tous** les individus ayant la meilleure (minimum) fitness pour chaque intervalle.

        :param interval_populations: Dictionnaire contenant la population de chaque intervalle
        :return: Dictionnaire des meilleurs individus par intervalle
        """

        best_individuals_per_interval = {}
        data_intervals = []

        intervals = self.split_intervals()
        for interval, parsed_data in intervals.items():
            data_intervals.append(parsed_data)

        for interval, population in interval_populations.items():
            scored_population = []

            # Calculer la fitness pour chaque individu
            for i, individual in enumerate(population):
                fitness = self.__calculate_fitnesses(data_intervals[interval], [individual])  # Méthode qui calcule la fitness
                scored_population.append((individual, fitness))

            if not scored_population:
                continue  # Sauter cet intervalle s'il est vide

            # Trouver la meilleure fitness obtenue (minimum)
            min_fitness = min(score[1] for score in scored_population)
            # Sélectionner **tous** les individus ayant cette meilleure fitness
            best_individuals = [ind[0] for ind in scored_population if ind[1] == min_fitness]
            # Sauvegarder les meilleurs individus pour cet intervalle
            best_individuals_per_interval[interval] = best_individuals
            print(best_individuals_per_interval)

        return best_individuals_per_interval
    
    def generate_shifted_population(self, best_individuals: Dict[int, List[List[List[DataStorage]]]], max_variants: int = 5) -> Dict[int, List[List[List[DataStorage]]]]:
        """
        Génère des individus identiques mais décalés dans le temps avec un `dt` constant.
        
        :param best_individuals: Meilleurs individus de chaque intervalle
        :param num_variants: Nombre de variantes à générer par individu
        :return: Dictionnaire contenant les populations de chaque intervalle après le décalage
        """
        shifted_populations = {}

        for interval, individuals in best_individuals.items():
            shifted_populations[interval] = []
            num_variants = min(max_variants, self.__population_size // len(best_individuals.get(interval, [1])))

            for individual in individuals:
                for i in range(num_variants):

                    dt = random.randint(-i * 100, i * 100) 
                    
                    shifted_individual = []
                    for commands in individual:
                        for command in commands:
                            new_time = command.time + dt
                            new_time = max(0, min(new_time, 3600))
                            shifted_aircraft = [
                                DataStorage(
                                    id=command.id,
                                    speed=command.speed,
                                    time=new_time  # Appliquer un décalage constant
                                )
                            ]
                            shifted_individual.append(shifted_aircraft)

                    shifted_populations[interval].append(shifted_individual)

        return shifted_populations
    

    def generate_final_population(self, shifted_populations: Dict[int, List[List[List[DataStorage]]]]) -> List[List[List[DataStorage]]]:
        """
        Génère une population complète en concaténant les individus de chaque intervalle.
        
        :param shifted_populations: Dictionnaire contenant les individus shiftés de chaque intervalle
        :param target_population_size: Taille maximale de la population finale
        :return: Liste d'individus représentant la population fusionnée
        """
        final_population = []

        # Déterminer le nombre de combinaisons possibles
        min_population_size = min(len(pop) for pop in shifted_populations.values())
        
        for _ in range(min_population_size):
            merged_individual = []

            for interval, population in shifted_populations.items():
                chosen_individual = random.choice(population)  # Prendre un individu aléatoire
                merged_individual.extend(chosen_individual)

            final_population.append(merged_individual)

        # Ajuster la taille de la population finale
        if len(final_population) > self.__population_size:
            final_population = final_population[:self.__population_size]

        return final_population
    
    def __select_parents(self, population: List[List[List[DataStorage]]], fitnesses: List[int]) -> List[List[List[DataStorage]]]:
        """Selection des parents dans la population en fonction des fitnesses"""
        total_fitness = sum(fitnesses)
        n = len(population)
        # Il faut au moins deux elements non nul pour tirer 2 elements
        # Il faut au moins k elements non nuls pour tirer k elements
        if fitnesses.count(0) >= n - 2:
            selected_indices = self.get_generator().choice(n, size=2, replace=False).tolist()
            return [population[i] for i in selected_indices] #np.random.sample(population, 2)
        
        #Pour un problème de min
        if self.is_minimisation :
            # Inverser la fitness pour la minimisation
            max_fitness = max(fitnesses)
            adjusted_fitnesses = [max_fitness - f for f in fitnesses]

            # Calcul des probabilités
            total_fitness = sum(adjusted_fitnesses)
            if total_fitness == 0 : 
                    probabilities = [1 / len(adjusted_fitnesses) for f in adjusted_fitnesses]
            else:
                probabilities = [f / (total_fitness) for f in adjusted_fitnesses]
        else: #Pour un problème de max
            if total_fitness == 0 :
                probabilities = [1 / len(fitnesses) for f in fitnesses]
            else : 
                probabilities = [f / (total_fitness) for f in adjusted_fitnesses]

        selected_indices = self.get_generator().choice(n, size=2, replace=False, p=probabilities).tolist()#random.choices(population, weights=probabilities, k=2)
        return [population[i] for i in selected_indices]
    
    def __crossover(self, parent1: List[List[DataStorage]], parent2: List[List[DataStorage]]) -> List[List[DataStorage]]:
        """Croisement d'individus entre deux parents"""
        offspring = []
        for traj1, traj2 in zip(parent1, parent2):
            if self.get_generator().random() < self.__crossover_rate:#random.random() < self.crossover_rate:
                point = self.get_generator().integers(low=1, high=len(traj1) - 1, endpoint=True) if len(traj1) > 1 else 1 #random.randint(1, len(traj1) - 1) if len(traj1) > 1 else 1
                child = deepcopy(traj1[:point]) + deepcopy(traj2[point:])
                offspring.append(child)
            else:
                offspring.append(deepcopy(traj1 if self.get_generator().random() < 0.5 else traj2))
        return offspring
        
    def __mutate(self, individual: List[List[DataStorage]]) -> List[List[DataStorage]]:
        """Mutation d'un individu"""
        new_individual = []
        for i, trajectory in enumerate(individual):
            new_trajectory = []
            asimulated_aircraft = self.get_data()[i]
            for j, data in enumerate(trajectory):
                if j == 0:  # Première commande (temps de départ et vitesse initiale)
                    if self.get_generator().random() < self.__mutation_rate * 2:

                        # updated_data = DataStorage(
                        #     speed=random.uniform(self.speed_min, self.speed_max),  # Nouvelle vitesse initiale
                        #     id=data.id,
                        #     time=max(data.time + random.uniform(-25.0, 25.0), 0.0),  # Temps de départ ajusté
                        #     heading=data.heading
                        # )
                        # Regenerer 
                        updated_data = asimulated_aircraft.generate_commands()[j]
                        new_trajectory.append(updated_data)
                    else:
                        new_trajectory.append(data)
                else:  # Autres commandes
                    if self.get_generator().random() < self.__mutation_rate:
                        # updated_data = DataStorage(
                        #     speed=random.uniform(self.speed_min, self.speed_max),
                        #     id=data.id,
                        #     time=data.time,
                        #     heading=data.heading
                        # )
                        
                        # trajectory est une liste de DataStorage representant des commandes pour l'asimulated_aircraft
                        # L'asimulated_aircraft genere donc une nouvelle liste de taille egale a la precedante
                        # mais data (element de trajectory) n'est pas forcement de la meme taille

                        updated_datas = asimulated_aircraft.generate_commands()

                        lower_bound   = max(min(len(updated_datas) - 1, 1), 0) # Tirage commande 1 ou plus si possible, 0 sinon
                        upper_bound   = len(updated_datas)
                        index_to_select = self.get_generator().integers(low=lower_bound, high=upper_bound, endpoint=False)
                        updated_data = asimulated_aircraft.generate_commands()[index_to_select]

                        new_trajectory.append(updated_data)
                    else:
                        new_trajectory.append(data)
            new_individual.append(new_trajectory)
        return new_individual


    def __next_population(self, population: List[List[List[DataStorage]]], fitnesses: List[float]) -> List[List[List[DataStorage]]]:
        """Calcul la prochaine population en fonction de la precedante et des valeurs de fitnesses"""
        next_population = []

        if (f == 0 for f in fitnesses) :
            return population
        else : 
            for _ in range(self.__population_size // 2):
                try:
                    parent1, parent2 = self.__select_parents(population, fitnesses)
                except Exception as e:
                    msg = f"Selection of parents in class {self.__class__.__name__} error\n{e}"
                    self.logger.error(msg)
                offspring1 = self.__crossover(parent1, parent2)
                offspring2 = self.__crossover(parent2, parent1)
                next_population.append(self.__mutate(offspring1))
                next_population.append(self.__mutate(offspring2))
            return next_population




    
    @override
    def run(self) -> List[List[DataStorage]]:
        try : 
            if self.is_verbose():
                self.logger.info(f"Il y a {len(self.get_data())} ASimulatedAircraft")

            self.set_process(0.)
            self.set_start_time(start=time())

            # Commencer les layer sur chaque intervalles
            interval_populations = {}
            # Parser les données
            intervals = self.split_intervals()
            for interval, parsed_data in intervals.items():
                population_layer : List[List[List[DataStorage]]] = None
                for layer in range(self.num_layers):
                    # couche 1 : maximiser l'ecartype 
                    # couche 2 : nombre de conflits en minimisant les changement temporelle des avions 
                    # couche 3 : ???
                    if not self.is_running():
                        break  
                    else : 
                        # On recommence les algorithme avec un liste de dataStorage qui contient tout le meilleurs individus  
                        best_solution, fitness, bests = self.run_genetic_on_interval(parsed_data, layer, population_layer)
                        n = self.interval_value

                        # Création de la prochaine population           
                        all_departure_times = [command.time for best in bests for aircraft in best for command in aircraft]  
                        first_departure = min(all_departure_times) if all_departure_times else float('inf')
                        last_departure = max(all_departure_times) if all_departure_times else float('inf')  
                        dt_interval = last_departure - first_departure
                        max_iter = self.layer_population_size[layer]

                        # Pour la diversité 
                        if population_layer is None:
                            population_layer = []
                        if len(bests) >= max_iter:
                            population_layer.extend(bests[:max_iter])  # Prend uniquement le nécessaire
                        else:
                            population_layer.extend(bests)  # Ajouter tous les meilleurs disponibles

                            # Complétion avec un `partial_shuffle` progressif
                            remaining_slots = max_iter - len(population_layer)
                            for i in range(remaining_slots):
                                dt = (dt_interval / n) * (i + 1)  # Augmentation progressive de dt
                                modified_solution = deepcopy(random.choice(bests))  # Copie aléatoire d'un meilleur individu
                                # Application du partial_shuffle avec dt croissant
                                modified_solution = self.partial_shuffle(modified_solution, dt, first_departure, last_departure)
                                population_layer.append(modified_solution)

                interval_populations[interval] = population_layer 
            
            #Pour chaque intervalle recuperer les meilleurs elements 
            best_individuals_per_interval = self.select_all_best_individuals(interval_populations) 
            #Pour chaque individus creer de nouveaux qui sont shifter dans le temps 
            best_individuals_shifted_interval = self.generate_shifted_population(best_individuals_per_interval)
            # Fusion des populations des intervalles pour créer la nouvelle population complète
            final_population = self.generate_final_population(best_individuals_shifted_interval)


            population      = final_population
            best_individual = None
            best_fitness    = None

            for generation in range(self.__generations):
                print(generation)
                if not self.is_running():
                    break  
                # Calcul fitnesses
                fitnesses = self.__calculate_fitnesses(self.get_data(), population, recalcul=False)
                
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
                self.set_process(int(((generation + 1) / self.__generations) * 100))
                self.set_process_time(process_time=time() - self.get_start_time())

                if self.is_verbose():
                    self.logger.info(f"Generation {generation + 1}: Progress = {self.get_progress()}%")
                print(best_fitness)
            self.stop()
            self.logger.info(f"Final Best Solution(fitness: {best_fitness}): {best_individual}")
            self.reinitialize_data()
            return best_individual
        except Exception as e :
            import traceback
            tb = traceback.format_exc()
            raise Exception(tb)

