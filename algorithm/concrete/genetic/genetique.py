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
    #@method_control_type(List[ASimulatedAircraft])
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
        self.best_results = [] # Garder en memoire les état avec la meme fitness
        self.best_fitness = None # Garder en memoire la meilleurs solution

        #Early Stopping : nombre d'individus dans la liste best_resultats avant d'arréter
        self.early_stopping = early_stopping

        # Attribut pour evité de generer un population initial
        self.__initial_population: List[List[List[DataStorage]]] = None, # setter

        # Autres attributs
        self.logger = setup_logging(self.__class__.__name__)


    def set_initial_population(self, initial_population : List[List[List[DataStorage]]] ) -> None :
        """ Initialise la population de l'algo genetique """
        self.__initial_population = initial_population

    def has_initial_population(self) ->bool :
        """ renvoie si la population de l'algo genetique est initialisé """
        return self.__initial_population != None

    def __generate_individuals(self, data: List[ASimulatedAircraft]) -> List[List[DataStorage]]:
        """Generation d'un individu (commandes) pour chaque ASimulatedAircraft"""
        return list(map(lambda obj: obj.initialize(), data))
    
    #@method_control_type(List[ASimulatedAircraft])
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
        """Selection des parents dans la population aleatoirement """
        n = len(population)
        if all(f == 0 for f in fitnesses):
            probabilities = [1 / len(fitnesses) for _ in fitnesses]
        else:
            if self.is_minimisation:
                max_fitness = max(fitnesses)
                adjusted_fitnesses = [max_fitness - f for f in fitnesses]
                total_fitness = sum(adjusted_fitnesses)
                probabilities = [f / total_fitness if total_fitness > 0 else 1 / len(adjusted_fitnesses) for f in adjusted_fitnesses]
            else:
                total_fitness = sum(fitnesses)
                probabilities = [f / total_fitness if total_fitness > 0 else 1 / len(fitnesses) for f in fitnesses]
         
        selected_indices = self.get_generator().choice(n, size=2, replace=False, p=probabilities).tolist()
        return [population[i] for i in selected_indices]
    
    def __select_parents_tournament(self, population: List[List[List[DataStorage]]], fitnesses: List[int]) -> List[List[List[DataStorage]]]:
        """Sélection par tournoi"""
        k = 5  # nombre d'individus tournoi
        indices = np.random.choice(len(population), k, replace=False)
        best_index = max(indices, key=lambda i: fitnesses[i]) if not self.is_minimisation() else min(indices, key=lambda i: fitnesses[i])
        return [population[best_index], population[np.random.choice(indices)]] #roulette aleatoire pour le deuxieme parent


    
    def __crossover(self, parent1: List[List[DataStorage]], parent2: List[List[DataStorage]]) -> List[List[DataStorage]]:
        """Croisement d'individus entre deux parents"""
        offspring = []
        for traj1, traj2 in zip(parent1, parent2):
            if self.get_generator().random() < self.__crossover_rate: #random.random() < self.crossover_rate:
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
                        # Regenerer 
                        updated_data = asimulated_aircraft.generate_commands()[j]
                        new_trajectory.append(updated_data)
                    else:
                        new_trajectory.append(data)
                else:  # On y passe que si on a plusieurs commandes
                    if self.get_generator().random() < self.__mutation_rate:

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

        if all(f == 0 for f in fitnesses) :
            return population
        else : 
            for _ in range(self.__population_size // 2):
                try:
                    parent1, parent2 = self.__select_parents(population, fitnesses)
                    offspring1 = self.__crossover(parent1, parent2)
                    offspring2 = self.__crossover(parent2, parent1)
                    next_population.append(self.__mutate(offspring1))
                    next_population.append(self.__mutate(offspring2))
                except Exception as e:
                    msg = f"Selection of parents in class {self.__class__.__name__} error\n{e}"
                    self.logger.error(msg)
                    return population

            return next_population
    
    def __next_population_elitism(self, population: List[List[List[DataStorage]]], fitnesses: List[float]) -> List[List[List[DataStorage]]]:
        """Calcul de la prochaine population avec élitisme et surproduction"""
        
        next_population = []
        
        # Sélection des élites
        elite_factor = 0.1 # 10%
        elite_size = max(1, int(elite_factor * self.__population_size)) 
        
        # Trier la population par fitness et garder les meilleurs
        sorted_indices = np.argsort(fitnesses) if self.is_minimisation() else np.argsort(fitnesses)[::-1]
        elites = [population[i] for i in sorted_indices[:elite_size]]
        
        next_population.extend(elites)  # Ajouter les élites à la nouvelle population
        
        # Génération des nouveaux individus
        while len(next_population) < self.__population_size:
            try:
                parent1, parent2 = self.__select_parents(population, fitnesses)
                offspring1 = self.__crossover(parent1, parent2)
                offspring2 = self.__crossover(parent2, parent1)
                next_population.append(self.__mutate(offspring1))
                if len(next_population) < self.__population_size:  
                    next_population.append(self.__mutate(offspring2))
            except Exception as e:
                self.logger.error(f"Erreur lors de la sélection des parents: {e}")
                return population  # En cas d'erreur, on ne change pas la population
        
        return next_population
    
    def __next_population_elitism_surprod(self, population: List[List[List[DataStorage]]], fitnesses: List[float]) -> List[List[List[DataStorage]]]:
        """Calcul de la prochaine population avec élitisme et surproduction"""
        
        next_population = []
        
        # Sélection des élites
        elite_factor = 0.1 # 10%
        elite_size = max(1, int(elite_factor * self.__population_size)) 
        sorted_indices = np.argsort(fitnesses) if self.is_minimisation() else np.argsort(fitnesses)[::-1]
        elites = [population[i] for i in sorted_indices[:elite_size]]  # Meilleurs individus actuels
        
        # Surproduction
        surprod_factor = 1.5 # 150% de la population cible
        surproduction_size = int(surprod_factor * self.__population_size) 
        temp_population = elites[:]  #copier les élites
        
        while len(temp_population) < surproduction_size:
            try:
                parent1, parent2 = self.__select_parents(population, fitnesses)
                offspring1 = self.__crossover(parent1, parent2)
                offspring2 = self.__crossover(parent2, parent1)
                temp_population.append(self.__mutate(offspring1))
                if len(temp_population) < surproduction_size:
                    temp_population.append(self.__mutate(offspring2))
            except Exception as e:
                self.logger.error(f"Erreur lors de la sélection des parents: {e}")
                return population  # En cas d'erreur, garder la population actuelle

        # Sélection finale des meilleurs individus pour la nouvelle génération
        new_fitnesses = self.__calculate_fitnesses(temp_population)
        sorted_indices = np.argsort(new_fitnesses) if self.is_minimisation() else np.argsort(new_fitnesses)[::-1]
        next_population = [temp_population[i] for i in sorted_indices[:self.__population_size]]

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

            # Mutation rate evolutif
            self.__mutation_rate = max(0.01, self.__mutation_rate * 0.99)  # Diminuer progressivement

            # Calcul fitnesses
            fitnesses = self.__calculate_fitnesses(population)
            #self.logger.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            # Acceptation ou non du critere
            if self.is_minimisation():
                optimal_fitness = min(fitnesses)
                if (generation <= 0) or (optimal_fitness < best_fitness) or (best_fitness == None):
                    # Maj variable locale
                    best_fitness   = optimal_fitness
                    best_individual = population[fitnesses.index(optimal_fitness)]
                    # Maj attribut
                    self.best_results = [best_individual]
                    self.best_fitness = best_fitness
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])
            else: # Maximisation
                optimal_fitness = max(fitnesses)
                if (generation <= 0) or (optimal_fitness > best_fitness) or (best_fitness == None):
                    # Maj variable locale
                    best_fitness    = optimal_fitness
                    best_individual = population[fitnesses.index(optimal_fitness)]
                    # Maj attribut
                    self.best_results = [best_individual]
                    self.best_fitness = best_fitness
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])

            # Logger
            if self.is_verbose():
                self.logger.info(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Best Individual = {best_individual}")

            # Maj du critiere
            self.set_best_critere(best_fitness)

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

        # Commencer avec une population predefinie
        if (not self.has_initial_population()): 
            population      = self.__generate_initial_population(self.get_data())
            best_individual = None
            best_fitness    = None
        else : 
            population = self.__initial_population
            fitnesses = self.__calculate_fitnesses(population)
            if self.is_minimisation():
                best_fitness = min(fitnesses)
            else : 
                best_fitness = max(fitnesses)
            best_individual = population[fitnesses.index(best_fitness)]
            self.best_results.append(best_individual)


        for generation in range(self.__generations):
            print(f"Génération {generation + 1}/{self.__generations}")
            # Calcul fitnesses
            fitnesses = self.__calculate_fitnesses(population)
            
           # self.logger.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            # Acceptation ou non du critere
            if self.is_minimisation():
                optimal_fitness = min(fitnesses)
                if (generation <= 0) or (optimal_fitness < best_fitness) or (best_fitness == None):
                    # Maj variable locale
                    best_fitness   = optimal_fitness
                    best_individual = population[fitnesses.index(optimal_fitness)]
                    # Maj attribut
                    self.best_results = [best_individual]
                    self.best_fitness = best_fitness
                elif optimal_fitness == best_fitness : 
                    self.best_results.append(population[fitnesses.index(optimal_fitness)])
            else: # Maximisation
                optimal_fitness = max(fitnesses)
                if (generation <= 0) or (optimal_fitness > best_fitness) or (best_fitness == None):
                    # Maj variable locale
                    best_fitness    = optimal_fitness
                    best_individual = population[fitnesses.index(optimal_fitness)]
                    # Maj attribut
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
        #self.reinitialize_data()
        return best_individual, best_fitness, self.best_results