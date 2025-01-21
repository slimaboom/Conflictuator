from copy import deepcopy
import random
from algorithm.recuit.data import DataStorage, ISimulatedObject
from typing import List, Optional
from algorithm.objective_function.IObjective import IObjective

from logging_config import setup_logging

class GeneticAlgorithm:
    def __init__(self, data: List[ISimulatedObject], 
                 evaluation_strategy: IObjective, 
                 population_size: int = 50, 
                 generations: int = 100, 
                 mutation_rate: float = 0.1, 
                 crossover_rate: float = 0.8):
        self.data = data
        self._data_saved = [deepcopy(d) for d in data]
        self.population_size: int = population_size
        self.generations: int = generations
        self.mutation_rate: float = mutation_rate
        self.crossover_rate: float = crossover_rate
        self._best_solution: Optional[List[DataStorage]] = None 
        self.speed_min = 0.001 
        self.speed_max = 0.0015 

        self.evaluation_strategy = evaluation_strategy


        self.loggerer = setup_logging(self.__class__.__name__)
        self._isrunning: bool = False 
        self._progress: float = 0


    def get_initial_data(self) -> List[ISimulatedObject]:
        return self._data_saved
    
    def generate_individuals(self, data: List[ISimulatedObject], max_changes: int) -> List[List[DataStorage]]:
        "Generation d'un individu"
        individual = []
        for obj in data:
            trajectory = []
            aircraft = obj.aircraft

            # Générer la première commande : temps de départ et vitesse initiale
            departure_time = max(aircraft.get_take_off_time() + random.uniform(0.0, 180.0), 0.0)  
            initial_speed = random.uniform(self.speed_min, self.speed_max)  
            trajectory.append(DataStorage(
                speed=initial_speed,
                id=obj.get_data_storage().id,
                time=round(departure_time, 2),
                heading=aircraft.get_heading()
            ))

            # Générer les autres commandes
            current_time = departure_time
            num_changes = random.randint(1, max_changes)  # Au moins un changement

            for _ in range(num_changes):
                speed = random.uniform(self.speed_min, self.speed_max)
                time = current_time + random.uniform(0.0, 120.0)  
                trajectory.append(DataStorage(speed=speed, id=obj.get_data_storage().id, time=round(time, 2)))
                current_time = time

            # Liste des changements ordonnée dans le temps
            trajectory.sort(key=lambda ds: ds.time)
            individual.append(trajectory)

        return individual

    
    def generate_initial_population(self, data: List[ISimulatedObject]) -> List[List[List[DataStorage]]]:
        population = []
        for _ in range(self.population_size):
            individual = self.generate_individuals(data, 5)
            population.append(individual)
        self.loggerer.info(f"Initial Population: {population}")
        return population

    
    def evaluate_fitness(self, individual: List[List[DataStorage]], data: List[ISimulatedObject]) -> float:
        # Critères
        total_conflicts = 0
        total_shared_time_bonus = 0
        total_time_difference_penalty = 0
        total_command_changes_penalty = 0
        total_speed_variation_penalty = 0
        total_command_spacing_penalty = 0

        dt_min = 150.0  # Espacement minimum entre commandes
        time_proximity_threshold = 30.0  # Seuil pour favoriser les rapprochements
        max_speed_variation = 0.0005  # Variation réaliste de vitesse

        # Calcul des autres critères
        for i, aircraft_sim in enumerate(data):
            trajectory = individual[i]
            aircraft = aircraft_sim.aircraft

            # Appliquer les commandes pour évaluer les conflits
            aircraft.set_take_off_time(trajectory[0].time)
            aircraft.set_speed(trajectory[0].speed)
            aircraft.set_commands(trajectory)
            total_conflicts = aircraft_sim.evaluate()  # Ajouter les conflits

            # Critères restants (comme avant)
            total_command_changes_penalty += len(trajectory)
            for j in range(1, len(trajectory)):
                speed_variation = abs(trajectory[j].speed - trajectory[j - 1].speed)
                if speed_variation > max_speed_variation:
                    total_speed_variation_penalty += speed_variation - max_speed_variation

                time_diff = trajectory[j].time - trajectory[j - 1].time
                if time_diff < dt_min:
                    total_command_spacing_penalty += dt_min - time_diff

        # Collecte des temps de passage pour toutes les balises
        balise_passages = {}
        for i, aircraft_sim in enumerate(data):
            aircraft = aircraft_sim.aircraft
            for balise_name, passage_time in aircraft.get_flight_plan_timed().items():
                if balise_name not in balise_passages:
                    balise_passages[balise_name] = []
                balise_passages[balise_name].append((i, passage_time))

       
        # Calcul des bonus/pénalités pour les temps de passage partagés
        for balise_name, passages in balise_passages.items():
            passages.sort(key=lambda x: x[1])  # Trier

            for j in range(len(passages) - 1):
                idx1, time1 = passages[j]
                idx2, time2 = passages[j + 1]

                # Vérifier si les avions partagent des balises sans conflit
                aircraft1 = data[idx1].aircraft
                aircraft2 = data[idx2].aircraft

                # Rapprochement temporel (bonus si les temps sont proches)
                time_diff = abs(time1 - time2)
                if time_diff <= time_proximity_threshold:
                    total_shared_time_bonus += time_proximity_threshold - time_diff  # Bonus fort pour temps rapprochés
                else:
                    total_time_difference_penalty += 0.5 * (time_diff - time_proximity_threshold)  # Pénalité légère si trop éloignés

        """ # Calcul des bonus/pénalités pour les temps de passage partagés
        for balise_name, passages in balise_passages.items():
            passages.sort(key=lambda x: x[1])  # Trier par temps de passage

            for j in range(len(passages) - 2):
                for u in range (j + 1, len(passages) - 1):
                    _, time1 = passages[j]
                    _, time2 = passages[u]

                    # Rapprochement temporel (bonus si les temps sont proches)
                    time_diff = abs(time1 - time2)
                    if time_diff <= time_proximity_threshold:
                        total_shared_time_bonus += time_proximity_threshold - time_diff  # Bonus fort pour temps rapprochés
                    else:
                        total_time_difference_penalty += 0.5 * (time_diff - time_proximity_threshold)  # Pénalité légère si trop éloignés"""



        # Pondérations des critères
        weights = {
            "conflicts": 100.0,
            "shared_time_bonus": 2.0,
            "time_difference_penalty": 2.0,
            "command_penalty": 1.0,
            "speed_penalty": 5.0,
            "spacing_penalty": 3.0,
        }

        # Calcul du score final
        fitness = (
            weights["conflicts"] * total_conflicts
            + weights["shared_time_bonus"] * total_shared_time_bonus
            - weights["time_difference_penalty"] * total_time_difference_penalty/360
            - weights["command_penalty"] * total_command_changes_penalty
            - weights["speed_penalty"] * total_speed_variation_penalty
            - weights["spacing_penalty"] * total_command_spacing_penalty/3600
        )

        return fitness



    def select_parents(self, population: List[List[List[DataStorage]]], fitnesses: List[int]) -> List[List[List[DataStorage]]]:
        total_fitness = sum(fitnesses)
        if total_fitness == 0:
            return random.sample(population, 2)
        probabilities = [f / total_fitness for f in fitnesses]
        return random.choices(population, weights=probabilities, k=2)

    def crossover(self, parent1: List[List[DataStorage]], parent2: List[List[DataStorage]]) -> List[List[DataStorage]]:
        offspring = []
        for traj1, traj2 in zip(parent1, parent2):
            if random.random() < self.crossover_rate:
                point = random.randint(1, len(traj1) - 1) if len(traj1) > 1 else 1
                child = deepcopy(traj1[:point]) + deepcopy(traj2[point:])
                offspring.append(child)
            else:
                offspring.append(deepcopy(traj1 if random.random() < 0.5 else traj2))
        return offspring
        
    def mutate(self, individual: List[List[DataStorage]]) -> List[List[DataStorage]]:
        new_individual = []
        for trajectory in individual:
            new_trajectory = []
            for i, data in enumerate(trajectory):
                if i == 0:  # Première commande (temps de départ et vitesse initiale)
                    if random.random() < self.mutation_rate * 2:
                        updated_data = DataStorage(
                            speed=random.uniform(self.speed_min, self.speed_max),  # Nouvelle vitesse initiale
                            id=data.id,
                            time=max(data.time + random.uniform(-25.0, 25.0), 0.0),  # Temps de départ ajusté
                            heading=data.heading
                        )
                        new_trajectory.append(updated_data)
                    else:
                        new_trajectory.append(data)
                else:  # Autres commandes
                    if random.random() < self.mutation_rate:
                        updated_data = DataStorage(
                            speed=random.uniform(self.speed_min, self.speed_max),
                            id=data.id,
                            time=data.time,
                            heading=data.heading
                        )
                        new_trajectory.append(updated_data)
                    else:
                        new_trajectory.append(data)
            new_individual.append(new_trajectory)
        return new_individual


    def run(self) -> List[List[DataStorage]]:
        self._isrunning = True
        self._progress = 0
        population = self.generate_initial_population(self.data)
        best_individual = None
        best_fitness = 0

        for generation in range(self.generations):
            if not self._isrunning:
                break  

            fitnesses = [self.evaluate_fitness(ind, self.data) for ind in population]

            self.loggerer.info(f"Generation {generation + 1} Fitnesses: {fitnesses}")

            max_fitness = max(fitnesses)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_individual = population[fitnesses.index(max_fitness)]

            self.loggerer.info(f"Generation {generation + 1}: Best Fitness = {best_fitness}, Best Individual = {best_individual}")

            next_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.select_parents(population, fitnesses)
                offspring1 = self.crossover(parent1, parent2)
                offspring2 = self.crossover(parent2, parent1)
                next_population.append(self.mutate(offspring1))
                next_population.append(self.mutate(offspring2))

            population = next_population

            self._progress = int(((generation + 1) / self.generations) * 100)
            self.loggerer.info(f"Generation {generation + 1}: Progress = {self._progress}%")

        self._isrunning = False

        self._best_solution = best_individual
        self.loggerer.info(f"Final Best Solution: {self._best_solution}")
        
        return self._best_solution

    def start(self) -> 'GeneticAlgorithm':
        self.run()
        self._reinitialize_data()
        return self

    def get(self) -> List[List[DataStorage]]:
        if self._best_solution is None:
            raise ValueError("No solution available. Run the algorithm first.")
        return self._best_solution

    def stop(self) -> None:
        self._isrunning = False

    def is_running(self) -> bool:
        return self._isrunning

    def get_progress(self) -> float:
        return self._progress

    def _reinitialize_data(self) -> None:
        for isimulatedobject, initial_isimulatedobject in zip(self.data, self.get_initial_data()):
            isimulatedobject.update(initial_isimulatedobject.get_data_storage().speed)