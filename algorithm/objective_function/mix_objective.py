
from typing import List
from algorithm.recuit.data import ISimulatedObject
from algorithm.storage import DataStorage
from algorithm.objective_function.IObjective import IObjective, ObjectiveError


# Evaluation combiné 
class CombinedEvaluationStrategy(IObjective):
    """ On maximise le nombre de conflit mais pour un meme nombre de conflit
    on va preferé ceux qui minimise le nombre de changement,
    qui reduit la variation de vitesse, 
    qui penalise les commandes trop proche en temps
    qui reduit le temps de croisement aux points de conflits """
    def __init__(self):
        self.individual = None
    
    def set_individual(self, individu: List[List[DataStorage]]) -> None:
        self.individual = individu

    def evaluate(self, data: List[ISimulatedObject]) -> float:
        if self.individual == None:
            msg = f"{self.__class__.__name__} attribute individual not set, please use set_individual method before using evaluate method"
            raise ObjectiveError(msg)
        
        total_conflicts = 0
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
            trajectory = self.individual[i]
            aircraft = aircraft_sim.aircraft

            # Appliquer les commandes pour évaluer les conflits
            #aircraft.set_take_off_time(trajectory[0].time)
            #aircraft.set_speed(trajectory[0].speed)
            #aircraft.set_commands(trajectory)
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