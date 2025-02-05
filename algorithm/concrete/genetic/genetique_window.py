import datetime
import random

import numpy as np
from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.concrete.genetic.genetique import AlgorithmGeneticBase
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from model.aircraft.storage import DataStorage
from logging_config import setup_logging
from utils.conversion import time_to_sec
from typing import List, Dict, Tuple
from typing_extensions import override
from copy import deepcopy
from datetime import datetime, time

@AAlgorithm.register_algorithm
class OptimizedGeneticAlgorithm(AlgorithmGeneticBase):
    
    def __init__(self, 
                 data: List['ASimulatedAircraft'],
                 is_minimise: bool = True,
                 verbose: bool = False,
                 population_size: int = 10,
                 generations: int = 10,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8,
                 interval_value: int = 5,
                 time_window: time = time(hour=0, minute=20, second=0),
                 **kwargs):
        
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, 
                         population_size=population_size, 
                         generations=generations,
                         mutation_rate=mutation_rate,
                         crossover_rate=crossover_rate,
                         **kwargs)        
        
        self.__time_window  = time_to_sec(time_window.isoformat())

        self.__interval_type: str = "group" # or'time'
        self.__interval_value = interval_value
    
    @override
    def set_layers(self, layers: List['AlgorithmGeneticBase']) -> None:
        """ Modifie la couche des layers en liste d'AlgorithmGeneticBase"""
        super().set_layers(layers)

    @override
    def get_layers(self) -> List[AlgorithmGeneticBase]:
        """Renvoie la couche des layers en liste d'AlgorithmGeneticBase"""
        return super().get_layers()
    
    def set_initial_population(self, initial_population : List[List[List[DataStorage]]] ) -> None :
        """ Initialise la population de l'algo genetique """
        self.__initial_population = initial_population

    def get_initial_population(self) -> List[List[List[DataStorage]]] :
        """ Renvoie la population de l'algorithme genetique """
        return self.__initial_population 
        

    def control_type_layers(self)->None:
        for i, layer_algo in enumerate(self.get_layers()) :
            self.logger.info(f"{layer_algo}, {isinstance(layer_algo, AlgorithmGeneticBase)}")
            if not isinstance(layer_algo, AlgorithmGeneticBase) : 
                error = f"Layer {i} must be an AlgorithmGeneticBase Type, got {type(layer_algo)}"
                raise TypeError(error)

    def split_intervals(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les données en intervalles temporels ou par groupes d'avions """
        if self.__interval_type == "time":
            return self.split_by_time()
        elif self.__interval_type == "group":
            return self.split_by_group()
        else:
            raise ValueError("interval_type must be 'time' or 'group'")
    
    def split_by_time(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les avions en fonction de leur temps de départ """
        num_intervals = int(self.get_simulation_duration() // self.__time_window)
        
        for obj in self.get_data():
            take_off_time = obj.get_object().get_commands()[0].time 
            interval_index = int(take_off_time // self.__time_window)
            
            if interval_index < num_intervals:
                #on remplit avec une deepcopy des avions
                self.aircraft_intervals[interval_index].append(obj)
        
        return self.aircraft_intervals
    
    def split_by_group(self) -> Dict[int, List['ASimulatedAircraft']]:
        """ Divise les avions en groupes de taille fixe et met le reste dans le dernier groupe """
        
        part = [self.get_data()[i:i+self.__interval_value] for i in range(0, len(self.get_data()), self.__interval_value)]
        self.aircraft_intervals = {i: [] for i in range(len(part))}
        for interval_index in range(len(part)):  # S'assure de ne pas dépasser la taille de `part`
            self.aircraft_intervals[interval_index] = part[interval_index]
        return self.aircraft_intervals


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
    
    def calculate_fitnesses_individual(self, individual: List[List[DataStorage]], parsed_data :List['ASimulatedAircraft']) -> List[float]:
        """Calcul les differentes fitnesses pour chaque individu de la population"""
        fitnesses = []
        for i, aircraft_sim in enumerate(parsed_data):
            trajectory = individual[i]
            # La liste de commandes est envoyer a l'avion et celui-ci met a jour son attribut et son TakeOffTime (premier element de la liste)
            # Les elements de self.get_data() sont modifies en place a travers la methode update_commands
            # ca re-calcul les differents conflits
            aircraft_sim.update_commands(trajectory)

        # A calculer apres avoir changer chaque avion 
        fitnesses.append(self.evaluate()) # Evaluation du critere avec la List[ASimulatedAircraft]
        return fitnesses
    

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
                fitness = self.calculate_fitnesses_individual(individual, data_intervals[interval])  # Méthode qui calcule la fitness
                scored_population.append((individual, fitness))

            if not scored_population:
                continue  # Sauter cet intervalle s'il est vide

            # Trouver la meilleure fitness obtenue (minimum)
            min_fitness = min(score[1] for score in scored_population)
            # Sélectionner **tous** les individus ayant cette meilleure fitness
            best_individuals = [ind[0] for ind in scored_population if ind[1] == min_fitness]
            # Sauvegarder les meilleurs individus pour cet intervalle
            best_individuals_per_interval[interval] = best_individuals

        return best_individuals_per_interval
    
    def generate_shifted_population(self, best_individuals: Dict[int, List[List[List[DataStorage]]]]) -> List[List[List[DataStorage]]]:
        """
        Génère une population complète en prenant un individu de best_individuals[0], 
        en ajustant le premier avion à t = interval * T / nb_intervals.
        
        :param best_individuals: Meilleurs individus de chaque intervalle
        :return: Liste contenant la population finale après les décalages
        """
        final_population = []
        T = self.get_simulation_duration()  # Durée totale de la simulation
        nb_intervals = len(best_individuals)

        for _ in range(self.get_population_size()):
            merged_individual = []

            for interval in range(nb_intervals):
                if best_individuals.get(interval):
                    chosen_individual = random.choice(best_individuals[interval])  # Sélection d'un individu aléatoire
                    
                    # Calcul du décalage de référence pour ce groupe
                    dt = (interval * T) / (nb_intervals-1)
                    
                    # Trouver le premier temps de départ de l'individu choisi
                    first_departure = min(command.time for commands in chosen_individual for command in commands)

                    shifted_individual = []
                    for commands in chosen_individual:
                        shifted_commands = []
                        for command in commands:
                            new_time = command.time - first_departure + dt  # Décalage en soustrayant le premier départ
                            new_time = max(0, min(new_time, self.get_simulation_duration()))
                            shifted_command = DataStorage(
                                id=command.id,
                                speed=command.speed,
                                time=new_time
                            )
                            shifted_commands.append(shifted_command)
                        shifted_individual.append(shifted_commands)

                    merged_individual.extend(shifted_individual)

            final_population.append(merged_individual)

        return final_population


    def create_population_with_layers(self) -> List[List[List[DataStorage]]]:
         # Commencer les layer sur chaque intervalles
        interval_populations = {}
        # Parser les données
        intervals = self.split_intervals()
        for j, (interval, parsed_data) in enumerate(intervals.items()):
            population_layer : List[List[List[DataStorage]]] = None
            
            progress = 100 * (j + 1 )/len(intervals)
            self.set_progress(round(progress  , 2))
            self.logger.info(f"Progress in creat_population_with_layers {progress} ({self.get_progress()})")
            for layer_num, layer_algo in enumerate(self.get_layers()):

                self.set_process_time(process_time=datetime.now().timestamp() - self.get_start_time())

                # couche 1 : maximiser l'ecartype 
                # couche 2 : nombre de conflits en minimisant les changement temporelle des avions 
                # couche 3 : ???
                if not self.is_running():
                    break  
                else :
                    layer_algo.set_data(parsed_data) #envoie des parsed data pour la layer consideré
                    # On recommence les algorithme avec un liste de dataStorage qui contient tout le meilleurs individus  
                    if not layer_algo.has_initial_population(): 
                        layer_algo.set_initial_population(population_layer)

                    _ = layer_algo.start()
                    best_individuals = layer_algo.get_best_results()
                    number_of_aircraft_per_window = self.__interval_value

                    self.set_best_fitness(layer_algo.get_best_fitness())

                    # Création de la prochaine population           
                    all_departure_times = [command.time for best in best_individuals for trajectory in best for command in trajectory]  
                    first_departure = min(all_departure_times) if all_departure_times else float('inf')
                    last_departure = max(all_departure_times) if all_departure_times else float('inf')  
                    dt_interval = last_departure - first_departure
                    max_iter = layer_algo.get_population_size()

                    # Pour la diversité 
                    if population_layer == None:
                        population_layer = []
                    if len(best_individuals) >= max_iter:
                        population_layer.extend(best_individuals[:max_iter])  # Prend uniquement le nécessaire
                    else:
                        population_layer.extend(best_individuals)  # Ajouter tous les meilleurs disponibles

                        # Complétion avec un `partial_shuffle` progressif
                        remaining_slots = max_iter - len(population_layer)
                        for i in range(remaining_slots):
                            dt = (dt_interval / number_of_aircraft_per_window) * (i + 1)  # Augmentation progressive de dt
                            modified_solution = random.choice(best_individuals) # Copie aléatoire d'un meilleur individu
                            # Application du partial_shuffle avec dt croissant
                            modified_solution = self.partial_shuffle(modified_solution, dt, first_departure, last_departure)
                            population_layer.append(modified_solution)

            interval_populations[interval] = population_layer 
            
        #Pour chaque intervalle recuperer les meilleurs elements 
        best_individuals_per_interval = self.select_all_best_individuals(interval_populations) 
        #Pour chaque individus creer de nouveaux qui sont shifter dans le temps 
        #best_individuals_shifted_interval = self.generate_shifted_population(best_individuals_per_interval)
        # Fusion des populations des intervalles pour créer la nouvelle population complète
        final_population = self.generate_shifted_population(best_individuals_per_interval)
        return final_population

    
    @override
    def run(self) -> List[List[DataStorage]]:
        try : 
            self.control_type_layers()
            if self.is_verbose():
                self.logger.info(f"Il y a {len(self.get_data())} ASimulatedAircraft")

            self.set_progress(0.)
            self.set_start_time(start=datetime.now().timestamp())

            # Récuperer la population final après les differente layers 
            final_population = self.create_population_with_layers()
            
            # algo genetique generale
            self.set_initial_population(final_population)
            #best_individual = self.run_algo_genetic(final_population)

            best_individual = super().run()
            self.set_best_critere(super().get_best_fitness())
            self.stop()
            self.logger.info(f"Final Best Solution(fitness: {self.get_best_fitness()}): {best_individual}")
            self.reinitialize_data()
            return best_individual
        
        except Exception as e :
            import traceback
            tb = traceback.format_exc()
            raise Exception(tb)

