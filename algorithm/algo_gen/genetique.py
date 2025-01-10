from copy import deepcopy
import random
from algorithm.recuit.data import DataStorage, ISimulatedObject
from typing import List, Optional

class GeneticAlgorithm:
    def __init__(self, data: List[ISimulatedObject], population_size: int = 50, generations: int = 100, mutation_rate: float = 0.1, crossover_rate: float = 0.8):
        self.data = data
        self._data_saved = [deepcopy(d) for d in data]
        self.population_size: int = population_size
        self.generations: int = generations
        self.mutation_rate: float = mutation_rate
        self.crossover_rate: float = crossover_rate
        self._best_solution: Optional[List[DataStorage]] = None 
        self.possible_speeds = [0.001, 0.002, 0.003, 0.0012]

        self.logger = self.setup_logger()
        self._isrunning: bool = False 
        self._progress: int = 0

    @staticmethod
    def setup_logger():
        import logging
        logger = logging.getLogger("GeneticAlgorithm")
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def get_initial_data(self) -> List[ISimulatedObject]:
        return self._data_saved

    def generate_initial_population(self, data: List[ISimulatedObject]) -> List[List[DataStorage]]:
        population = []
        for _ in range(self.population_size):
            individual = [
                DataStorage(speed=random.choice(self.possible_speeds), id=obj.get_data_storage().id)
                for obj in data
            ]
            population.append(individual)
        self.logger.info(f"Initial Population: {population}")
        return population

    def evaluate_fitness(self, individual: List[DataStorage], data: List[ISimulatedObject]) -> int:
        conflicts = 0
        for i, obj in enumerate(data):
            obj.update(individual[i].speed)
            conflicts += obj.evaluate()
        return conflicts/2

    def select_parents(self, population: List[List[DataStorage]], fitnesses: List[int]) -> List[List[DataStorage]]:
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            return random.sample(population, 2)
        probabilities = [f / total_fitness for f in fitnesses]
        return random.choices(population, weights=probabilities, k=2)

    def crossover(self, parent1: List[DataStorage], parent2: List[DataStorage]) -> List[DataStorage]:
        if len(parent1) <= 1 or len(parent2) <= 1:
            return parent1 if random.random() < 0.5 else parent2

        if random.random() < self.crossover_rate:
            point = random.randint(1, len(parent1) - 1)
            offspring = parent1[:point] + parent2[point:]
            return [DataStorage(speed=gene.speed, id=gene.id) for gene in offspring]
        return [DataStorage(speed=gene.speed, id=gene.id) for gene in parent1]

    def mutate(self, individual: List[DataStorage]) -> List[DataStorage]:
        for gene in individual:
            if random.random() < self.mutation_rate:
                individual = [
                    DataStorage(speed=random.choice(self.possible_speeds), id=gene.id) 
                    for gene in individual
                ]
        return individual

    def run(self) -> List[DataStorage]:
        self._isrunning = True
        self._progress = 0
        population = self.generate_initial_population(self.data)
        best_individual = None
        best_fitness = 0

        for generation in range(self.generations):
            if not self._isrunning:
                break  

            fitnesses = [self.evaluate_fitness(ind, self.data) for ind in population]

            self.logger.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            max_fitness = max(fitnesses)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_individual = population[fitnesses.index(max_fitness)]

            self.logger.info(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Best Individual = {best_individual}")

            next_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.select_parents(population, fitnesses)
                offspring1 = self.crossover(parent1, parent2)
                offspring2 = self.crossover(parent2, parent1)
                next_population.append(self.mutate(offspring1))
                next_population.append(self.mutate(offspring2))

            population = next_population

            self._progress = int(((generation + 1) / self.generations) * 100)
            self.logger.info(f"Generation {generation + 1}: Progress = {self._progress}%")

        self._isrunning = False

        self._best_solution = best_individual
        self.logger.info(f"Final Best Solution: {self._best_solution}")
        return self._best_solution

    def start(self) -> 'GeneticAlgorithm':
        self.run()
        self._reinitialize_data()
        return self

    def get(self) -> List[DataStorage]:
        if self._best_solution is None:
            raise ValueError("No solution available. Run the algorithm first.")
        return self._best_solution

    def stop(self) -> None:
        self._isrunning = False

    def is_running(self) -> bool:
        return self._isrunning

    def get_progress(self) -> int:
        return self._progress

    def _reinitialize_data(self) -> None:
        for isimulatedobject, initial_isimulatedobject in zip(self.data, self.get_initial_data()):
            isimulatedobject.update(initial_isimulatedobject.get_data_storage().speed)
