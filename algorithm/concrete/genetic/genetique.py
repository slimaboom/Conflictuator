from algorithm.interface.IAlgorithm import AAlgorithm
from algorithm.interface.ISimulatedObject import ASimulatedAircraft
from model.aircraft.storage import DataStorage
from logging_config import setup_logging

from utils.controller.argument import method_control_type

from typing import List
from typing_extensions import override
from copy import deepcopy
from datetime import time, datetime
import numpy as np

@AAlgorithm.register_algorithm
class AlgorithmGenetic(AAlgorithm):
    @method_control_type(List[ASimulatedAircraft])
    def __init__(self, data: List[ASimulatedAircraft], 
                 is_minimise: bool = False,
                 verbose    : bool = False,
                 timeout: time = time(hour=0, minute=2, second=0),
                 population_size: int = 50, 
                 generations: int = 100, 
                 mutation_rate: float = 0.1, 
                 crossover_rate: float = 0.8,
                 early_stopping: int = 10,
                 **kwargs):
        
        # Attributs generaux
        super().__init__(data=data, is_minimise=is_minimise, verbose=verbose, 
                         timeout=timeout,
                         **kwargs)

        # Paramètre de l'algorithme génétique
        # les définir pour les rendre compatible a l'optimisation
        self.__population_size = population_size
        self.__generations     = generations
        self.__mutation_rate   = mutation_rate
        self.__crossover_rate  = crossover_rate

        # Attribut pour sauvegarder les meilleurs résultats
        self.best_results = []
        self.best_fitness = None
        self.early_stopping = early_stopping

        # Autres attributs
        self.logger = setup_logging(self.__class__.__name__)


    def __generate_individuals(self, data: List[ASimulatedAircraft]) -> List[List[DataStorage]]:
        """Generation d'un individu (commandes) pour chaque ASimulatedAircraft"""
        return list(map(lambda obj: obj.initialize(), data))
    
    @method_control_type(List[ASimulatedAircraft])
    def __generate_initial_population(self, data: List[ASimulatedAircraft]) -> List[List[List[DataStorage]]]:
        """Generation d'une population initiale.
            C'est pour chaque element de data, il y a generation d'individus (de plusieurs jeux de commandes pour chaque ASimulatedAircraft)
        """
        population = []
        for _ in range(self.__population_size):
            individual = self.__generate_individuals(data)
            population.append(individual)

        if self.is_verbose():
            self.logger.info(f"Initial Population: {population}")
        return population


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

    def __calculate_fitnesses(self, population: List[List[List[DataStorage]]]) -> List[float]:
        """Calcul les differentes fitnesses pour chaque individu de la population"""
        fitnesses = []
        for individual in population:
            for i, aircraft_sim in enumerate(self.get_data()):
                trajectory = individual[i]
                # La liste de commandes est envoyer a l'avion et celui-ci met a jour son attribut et son TakeOffTime (premier element de la liste)
                # Les elements de self.get_data() sont modifies en place a travers la methode update_commands
                # ca re-calcul les differents conflits
                aircraft_sim.update_commands(trajectory)

            # A calculer apres avoir changer chaque avion 
            fitnesses.append(self.evaluate()) # Evaluation du critere avec la List[ASimulatedAircraft]
        return fitnesses

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
        if self.is_verbose():
            self.logger.info(f"Il y a {len(self.get_data())} ASimulatedAircraft")

        self.set_process(0.)
        self.set_start_time(start=datetime.now().timestamp())

        population      = self.__generate_initial_population(self.get_data())
        best_individual = None
        best_fitness    = None

        for generation in range(self.__generations):
            if not self.is_running():
                break  

            # Calcul fitnesses
            fitnesses = self.__calculate_fitnesses(population)
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
            self.set_process_time(process_time=datetime.now().timestamp() - self.get_start_time())

            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Progress = {self.get_progress()}%")

        self.stop()
        self.logger.info(f"Final Best Solution(fitness: {best_fitness}): {best_individual}")
        self.reinitialize_data()
        return best_individual
    

    # Meme methode que run mais ne declanche pas la queue
    def startbis(self) -> List[List[DataStorage]]:
        if self.is_verbose():
            self.logger.info(f"Il y a {len(self.get_data())} ASimulatedAircraft")

        self.set_process(0.)
        self.set_start_time(start=datetime.now().timestamp())

        population      = self.__generate_initial_population(self.get_data())
        best_individual = None
        best_fitness    = None

        for generation in range(self.__generations):
            print(f"Génération {generation + 1}/{self.__generations}")
        

            # Calcul fitnesses
            fitnesses = self.__calculate_fitnesses(population)
           # self.logger.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            # Acceptation ou non du critere
            if self.is_minimisation():
                optimal_fitness = min(fitnesses)
                if (generation <= 0) or (optimal_fitness < best_fitness) or (best_fitness == None):
                    best_fitness   = deepcopy(optimal_fitness)
                    best_individual = deepcopy(population[fitnesses.index(optimal_fitness)])
                    self.best_results = [best_individual]
                    self.best_fitness = best_fitness
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])
            else: # Maximisation
                optimal_fitness = max(fitnesses)
                if (generation <= 0) or (optimal_fitness > best_fitness) or (best_fitness == None):
                    best_fitness   = deepcopy(optimal_fitness)
                    best_individual = deepcopy(population[fitnesses.index(optimal_fitness)])
                    self.best_results = [best_individual]
                    self.best_fitness = best_fitness
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])

            # Logger
            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Best Individual = {best_individual}")

            # Calcul de la Prochaine population
            population = self.__next_population(population, fitnesses)

            # Avancement du processus
            self.set_process(int(((generation + 1) / self.__generations) * 100))
            self.set_process_time(process_time=datetime.now().timestamp() - self.get_start_time())

            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Progress = {self.get_progress()}%")
            
            # Early stopping après avoir plusieurs individu avec une fitness de 0 
            # Uniquement pour les minimisations
            if (self.early_stopping != None) and (len(self.best_results) > self.early_stopping) and (self.best_fitness == 0) and self.is_minimisation :
                break

        #self.stop()
        self.logger.info(f"Final Best Solution(fitness: {best_fitness}): {best_individual}")
        self.reinitialize_data()
        return best_individual, best_fitness