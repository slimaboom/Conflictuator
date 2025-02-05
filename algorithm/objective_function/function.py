from algorithm.interface.IObjective import AObjective
from algorithm.interface.ISimulatedObject import ASimulatedAircraft

from typing import List
from typing_extensions import override

import numpy as np
#-------------------------------------------------#
# Implementation de l'interface des fonctions objectives

#----------------------------------------------------------
#----------------------------------------------------------
#------------- ObjectiveFunctionMaxConflict ---------------
#----------------------------------------------------------
#----------------------------------------------------------
@AObjective.register_objective_function
class ObjectiveFunctionMaxConflict(AObjective):
    """ 
    Fonction objective simple:
    calculant le nombre de conflits de chaque ASimulatedAircraft
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @override
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        total_conflicts = 0
        nc = 0.
        for _, aircraft_sim in enumerate(data):
            for conflicts in aircraft_sim.get_object().get_conflicts().get_all().values():
                nc = len(conflicts)
                total_conflicts += nc
        return (total_conflicts * 0.5)
    
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#------------- ObjectiveFunctionMaxConflictMinVariation ----------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
@AObjective.register_objective_function
class ObjectiveFunctionMaxConflictMinVariation(AObjective):
    """ Fonction objective:
            calculant le nombre de conflits de chaque ASimulatedAircraft
             - en reduisant l'ecart temporelle entre les conflits aux points de conflits
             - en reduisant la variation de vitesse entre deux ASimulatedAircraft
             - en pénalisant les variations de commandes trop proche en temps
             - en pénalisant les ASimulatedAircraft qui ont trop de commandes.
        
        Un bon ASimulatedAircraft est:
            - ecart temporelle réduit avec un autre sur une meme balise conflictuelle
            - des variations de vitesses pas trop importante
            - un nombre de commande pas trop important
            - deux commandes successives éloignés d'une duree minimale (pas trop rapprochés)
    """
    def __init__(self, weight_conflicts: float = 100.0,
                       weight_shared_time_bonus: float = 2.0,
                       weight_time_difference_penalty: float = 1.0,
                       weight_speed_penality: float = 5.0,
                       weight_spacing_penality: float = 3.0,
                       weight_command_penality: float = 1.0,
                       threshold_min_time_variation_command: float = 150.,
                       threshold_max_time_proximity: float = 30.0,
                       threshold_speed_variation: float = 0.0005,
                       **kwargs):
        """
        Constructeur de la classe ObjectiveFunctionMaxConflictMinVariation.

        @param weight_conflicts: float, optionnel
            Poids associé à la pénalisation des conflits entre les ASimulatedAircraft. 
            Plus ce poids est élevé, plus l'algorithme cherchera les conflits. Par défaut 100.0.

        @param weight_shared_time_bonus: float, optionnel
            Bonus attribué pour réduire l'écart temporel entre deux ASimulatedAircraft sur un même point conflictuel. Par défaut 2.0.
       
        @param weight_time_difference_penalty: float, optionnel
            Pénalité appliquée pour les écarts temporels significatifs entre les conflits. Par défaut 1.0.

        @param weight_speed_penality: float, optionnel
            Pénalité appliquée aux variations importantes de vitesse entre deux ASimulatedAircraft. Par défaut 5.0.

        @param weight_spacing_penality: float, optionnel
            Pénalité appliquée lorsque deux commandes successives sont trop proches dans le temps. Par défaut 3.0.

        @param weight_command_penality: float, optionnel
            Pénalité appliquée lors qu'il y a trop de commandes pour un ASimulatedAircraft
            
        @param threshold_min_time_variation_command: float, optionnel
            Seuil minimal de temps (en secondes) entre deux commandes successives pour éviter la pénalisation. Par défaut 150.0 (2min30).
            Espacement minimum entre commandes

        @param threshold_max_time_proximity: float, optionnel
            Seuil maximal de proximité temporelle (en secondes) pour déterminer si deux ASimulatedAircraft sont trop proches dans le temps sur un même point conflictuel. Par défaut 30.0.
            Si l'écart temporelle entre deux ASimulatedAircraft est inférieur aux seuil alors c'est bonifié (bonne situation) 
            Seuil pour favoriser les rapprochements
        @param threshold_speed_variation: float, optionnel
            Seuil de variation de vitesse entre deux commandes (exprimée en pourcentage entre 0 et 100) au-delà duquel une pénalité est appliquée. Par défaut 25% (0.0005).

        
            
        @attribute __weight_conflicts: float
            Poids pour pénaliser les conflits.
        @attribute __weight_shared_time_bonus: float
            Bonus pour réduire l'écart temporel sur les points conflictuels.
        @attribute __weight_time_difference_penalty: float
            Pénalité pour des écarts temporels entre les conflits.
        @attribute __weight_speed_penality: float
            Pénalité pour les variations de vitesse.
        @attribute __weight_spacing_penality: float
            Pénalité pour des commandes successives trop rapprochées.
        @attribute __threshold_min_time_variation_command: float
            Seuil minimal de temps entre deux commandes.
        @attribute __threshold_max_time_proximity: float
            Seuil de proximité temporelle entre deux ASimulatedAircraft.
        @attribute __threshold_speed_variation: float
            Seuil de variation de vitesse à ne pas dépasser.

        Cette classe permet de définir et d'ajuster les paramètres nécessaires pour évaluer et optimiser les trajectoires des ASimulatedAircraft maximisant les conflits tout en minimisant les variations de vitesse et les commandes rapprochées dans le temps.
        """

        super().__init__(**kwargs)

        # Weights used for evaluation
        self.__weight_conflicts               = weight_conflicts
        self.__weight_shared_time_bonus       = weight_shared_time_bonus
        self.__weight_time_difference_penalty = weight_time_difference_penalty
        self.__weight_speed_penality          = weight_speed_penality
        self.__weight_spacing_penality        = weight_spacing_penality
        self.__weight_command_penality        = weight_command_penality

        # Threshold used for evaluation for counting penality
        self.__threshold_min_time_variation_command = threshold_min_time_variation_command
        self.__threshold_max_time_proximity         = threshold_max_time_proximity
        self.__threshold_speed_variation            = threshold_speed_variation

    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        """
            Score Formula: `y = f(data)`

            ```
            y = max(0, 
                  weights["conflicts"] * total_conflicts
                + weights["shared_time_bonus"] * total_shared_time_bonus
                - weights["time_difference_penalty"] * total_time_difference_penalty / 360
                - weights["command_penalty"] * total_command_changes_penalty
                - weights["speed_penalty"] * total_speed_variation_penalty
                - weights["spacing_penalty"] * total_command_spacing_penalty / 3600
            ```
        """
        
        # Critères
        total_conflicts = 0
        total_shared_time_bonus = 0
        total_time_difference_penalty = 0
        total_command_changes_penalty = 0
        total_speed_variation_penalty = 0
        total_command_spacing_penalty = 0

        # Collecte des temps de passage pour toutes les balises
        balise_passages = {}

        for _, asimulated_aircraft in enumerate(data):
            commands = asimulated_aircraft.get_data_storages()
            num_commands = len(commands)

            total_conflicts += len(asimulated_aircraft.get_object().get_conflicts())

            if num_commands >= 2: # Favoriser ceux avec peu de commandes donc on ajoute pas si moins de 1 commandes
                total_command_changes_penalty += num_commands
                # Il faut au moins deux commandes
                for j in range(1, num_commands):
                    # Ecart entre nouvelle vitesse et precedante
                    # La reference est la vitesse precedante pour le calcul
                    #rapport = commands[j - 1].speed/commands[j].speed
                    #relative_speed_variation = abs(1 - rapport)

                    relative_speed_variation = abs(commands[j].speed - commands[j - 1].speed)

                    if relative_speed_variation > self.__threshold_speed_variation:
                        total_speed_variation_penalty += relative_speed_variation - self.__threshold_speed_variation

                time_diff = commands[j].time - commands[j - 1].time
                if time_diff < self.__threshold_min_time_variation_command:
                    total_command_spacing_penalty += self.__threshold_min_time_variation_command - time_diff


            aircraft = asimulated_aircraft.get_object()
            # Collecte des temps de passage pour toutes les balises
            for balise_name, passage_time in aircraft.get_flight_plan_timed().items():
                if balise_name not in balise_passages:
                    balise_passages[balise_name] = []
                balise_passages[balise_name].append((aircraft, passage_time))
        # end for data

        # Calcul des bonus/pénalités pour les temps de passage partagés
        for balise_name, passages in balise_passages.items():
            passages.sort(key=lambda x: x[1])  # Trier

            for j in range(len(passages) - 1):
                aircraft_first, time_first   = passages[j]
                aircraft_second, time_second = passages[j + 1]

                # Rapprochement temporel (bonus si les temps sont proches)
                time_diff = abs(time_first - time_second)
                if time_diff <= self.__threshold_max_time_proximity:
                     # Bonus fort pour temps rapprochés
                    total_shared_time_bonus += self.__threshold_max_time_proximity - time_diff  # Bonus fort pour temps rapprochés
                else:
                    # Pénalité légère si trop éloignés
                    total_time_difference_penalty += 0.5 * (time_diff - self.__threshold_max_time_proximity)

        # Calcul du score final
        conflict_value   = self.__weight_conflicts * total_conflicts
        time_bonus_value = self.__weight_shared_time_bonus * total_shared_time_bonus
        
        timediff_penality_value = self.__weight_time_difference_penalty *  total_time_difference_penalty/360
        command_penality_value  = self.__weight_command_penality * total_command_changes_penalty
        speed_penalty_value     = self.__weight_speed_penality * total_speed_variation_penalty
        spacing_penalty_value   = self.__weight_spacing_penality * total_command_spacing_penalty/3600

        fitness  = conflict_value + time_bonus_value 
        fitness +=- (timediff_penality_value + command_penality_value + speed_penalty_value + spacing_penalty_value)
        return fitness # s'assurer que la fitness est positive.
    


    


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#------------- ObjectiveFunctionExactConflict --------------------------
#---------------- PENALISATION EXTERNAL --------------------------------
#-----------------------------------------------------------------------
@AObjective.register_objective_function 
class ObjectiveFunctionConflictInternal(AObjective):

    def __init__(self,
                nb_expected_conflict: int = 2,
                nb_expected_balise :int = 2,
                weight_conflicts: float = 1,
                weight_external_penality: float= 0.01,
                weight_balise: float = 0.1,
                **kwargs):

        super().__init__(**kwargs)

        # Nombre de conflit voulu
        self.nb_expected_conflict: int = nb_expected_conflict
        self.nb_expected_balise: int = nb_expected_balise

        # Bonus et penalisation
        self.__weight_conflicts = weight_conflicts
        self.__weight_external_penality = weight_external_penality
        self.__weight_conflicts = weight_conflicts
        self.__weight_balise = weight_balise

    def set_nb_expected_conflict(self, n: int) -> None:
        self.nb_expected_conflict = n
    
    @override
    def evaluate(self, data: List[ASimulatedAircraft]) -> float:
        total_conflicts = 0
        nc = 0.
        conflict = []
        conflict_pair = []
        conflict_balise = []
        external_penalisation = 0
        redundance_penalisation = 0
        for _, aircraft_sim in enumerate(data):
            for conflicts in aircraft_sim.get_object().get_conflicts().get_all().values():
                if conflicts not in conflict:
                    conflict.append(conflicts)
                    nc = len(conflicts)
                    total_conflicts += nc

                    for c in conflicts : 
                        if c.location not in conflict_balise :
                            conflict_balise.append(c.location)
                        if c.conflict_time_one >c.conflict_time_two : 
                            if (c.aircraft_two, c.aircraft_one)  not in conflict_pair :
                                conflict_pair.append((c.aircraft_two, c.aircraft_one))
                            else :
                                redundance_penalisation += 1
                        else : 
                            if (c.aircraft_one, c.aircraft_two)  not in conflict_pair :
                                conflict_pair.append((c.aircraft_one, c.aircraft_two))
                            else : 
                                redundance_penalisation += 1
                        if c.location.is_external() == True:
                            external_penalisation += 1


        # Calcul du coût : 
        penalisation = self.__weight_external_penality * external_penalisation
        conflicts    = np.abs(self.nb_expected_conflict - (total_conflicts * 0.5)) * self.__weight_conflicts
        penality_balise = abs(self.nb_expected_balise - len(conflict_balise)) * self.__weight_balise
        red_penalisation =  self.__weight_balise / 2 * redundance_penalisation

        total = conflicts + penalisation + penality_balise + red_penalisation
        return total
    
    


#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#------------- Calcul de l'ecartype des temps des avions ---------------
#---------------- décollant dans une fenetre temporelle-----------------
#-----------------------------------------------------------------------

@AObjective.register_objective_function 
class ObjectiveFunctionTimeStdDev(AObjective):
    """
    Fonction objective calculant l'écart-type des temps de passage aux balises
    pour les avions ayant décollé entre t1 et t2.
    """
    def __init__(self):
        """
        Initialise la fonction objective avec une fenêtre temporelle.
        
        :param time_window_start: float, début de la fenêtre temporelle
        :param time_window_end: float, fin de la fenêtre temporelle
        """
        super().__init__()

        # Calcul des temps de la fenetre temporelle sur lequelle on 
    

    @override
    def evaluate(self, data: List[ASimulatedAircraft] = None) -> float:
        """
        Calcule la somme des écarts-types des temps de passage aux balises en prenant toutes les combinaisons possibles de 3 avions.
        Utile pour un génétique qui maximise l'écart-type.
        
        :param data: Liste des avions simulés
        :return: Somme des écarts-types des temps de passage par groupes de 3
        """
        import numpy as np
        from itertools import combinations
        
        departure_times = [aircraft.get_object().get_commands()[0].time for aircraft in data]
        first_departure = min(departure_times) if departure_times else float('inf') 
        last_departure = max(departure_times) if departure_times else float('inf') 

        self.time_window_start = first_departure
        self.time_window_end = last_departure

        if len(departure_times) < 3:
            return 0.0  # Pas assez de données pour un calcul significatif
        
        # Calcul de la somme des écarts-types pour toutes les combinaisons possibles de 3 avions
        std_sum = sum(np.std(comb) for comb in combinations(departure_times, 3))
        
        return std_sum
    
