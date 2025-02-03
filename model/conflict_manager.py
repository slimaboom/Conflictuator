from dataclasses import dataclass

import numpy as np

from logging_config import setup_logging

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from model.aircraft.aircraft import Aircraft
    from model.balise import Balise

@dataclass(frozen=True)
class ConflictInformation:
    aircraft_one: 'Aircraft'
    aircraft_two: 'Aircraft'
    conflict_time_one: float
    conflict_time_two: float
    location: 'Balise'

    @property
    def time_difference(self) -> float:
        """Calcule la différence de temps entre les deux avions."""
        return self.conflict_time_two - self.conflict_time_one

    @property
    def distance_to_balise(self):
        """Calcul la distance:
            - entre la balise et l'avion 1
            - entre la balise et l'avion 2
        """
        distance_one = self.aircraft_one.get_position().distance_horizontale(self.location)
        distance_two = self.aircraft_two.get_position().distance_horizontale(self.location)
        return distance_one, distance_two
    
    def get_aircraft_one(self): return self.aircraft_one
    def get_aircraft_two(self): return self.aircraft_two

    def get_conflict_time_one(self): return self.conflict_time_one
    def get_conflict_time_two(self): return self.conflict_time_two
    
    def get_location(self): return self.location
    def get_time_difference(self): return self.time_difference
    
    def __repr__(self):
        id_one = self.aircraft_one.get_id_aircraft()
        id_two = self.aircraft_two.get_id_aircraft()
        speed_one = self.aircraft_one.get_speed()
        speed_two = self.aircraft_two.get_speed()
        return f"ConflictInformation(id_one={id_one} (v={speed_one}), id_two={id_two} (v={speed_two}), time_one={self.conflict_time_one}, time_two={self.conflict_time_two}, location=\'{self.location.get_name()}\')"


class ConflictManager:
    """Manager responsable de la détection et de la gestion des conflits."""
    logger = setup_logging("ConflictManager")

    def __init__(self, time_threshold: float = 60):
        self.aircrafts = {}
        self.balises = {}
        self.time_threshold = time_threshold
        self.time_simulation = None
        self.conflicts: List[ConflictInformation] = []

    def register_aircraft(self, aircraft: 'Aircraft') -> None:
        """Enregistre un avion dans le gestionnaire."""
        self.aircrafts[aircraft.get_id_aircraft()] = aircraft
        self.detect_conflicts(list(self.aircrafts.values()))  # recalculer les conflits car certains peuvent apparaitre

    def register_balise(self, balise: 'Balise') -> None:
        """Enregistre une balise dans le gestionnaire."""
        self.balises[balise.get_name()] = balise

    def delete_aircraft(self, aircraft: 'Aircraft') -> bool:
        aircraft_id = aircraft.get_id_aircraft()
        if self.aircrafts.get(aircraft_id):
            del self.aircrafts[aircraft_id]
            self.detect_conflicts(list(self.aircrafts.values())) # recalculer les conflits car certains peuvent disparaitre
            return True
        else: return False

    def set_time_simulation(self, time: float) -> None:
        self.time_simulation = time

    def update_aircraft_conflicts(self, updated_aircraft: 'Aircraft') -> None:
        """
        Met à jour les conflits impliquant un avion spécifique après une modification.
        """
        # Récupérer les balises affectées par cet avion
        affected_balises = updated_aircraft.get_flight_plan_timed().keys()
        
        # Identifier les avions partageant ces balises
        impacted_aircrafts = []
        for aircraft in self.aircrafts.values():
            if any(balise in aircraft.get_flight_plan_timed() for balise in affected_balises):
                impacted_aircrafts.append(aircraft)
        
        # Ajouter l'avion cible en tête de la liste
        impacted_aircrafts.insert(0, updated_aircraft)

        # Supprimer les doublons tout en maintenant l'ordre
        impacted_aircrafts = list(dict.fromkeys(impacted_aircrafts))
        
        # Recalculer les conflits uniquement pour ces avions
        self.detect_conflicts(impacted_aircrafts)



    def detect_conflicts(self, aircraft_list: List['Aircraft']) -> None:
        """
        Détecte les conflits de passage par les balises.
        Retourne un dictionnaire où chaque balise est associée à une liste de conflits.
        """
        #self.logger.info(f"Calcul des conflits pour:  {[aircraft.get_id_aircraft() for aircraft in aircraft_list]}")

        # Sécurité quand on supprimer des avions, ça recalcul les conflits et si la liste est vide il y a plus rien
        # SimulationViewController.cleanup() appelle Simulation.delete_aircraft
        if not aircraft_list: return aircraft_list
        
        # Identifier l'avion cible 
        target_aircraft = aircraft_list[0]
        target_id = target_aircraft.get_id_aircraft()

        # Obtenir les IDs des avions impactés
        impacted_aircraft_ids = {aircraft.get_id_aircraft() for aircraft in aircraft_list}

        # Étape 1 : Nettoyer les conflits pour chaque avion impliqué
        for i, aircraft in enumerate(aircraft_list):
            if (aircraft.get_id_aircraft() != target_id):
                aircraft.clear_conflicts(target_id)
            target_aircraft.clear_conflicts(aircraft)
        
        # Collecter les temps de passage pour chaque avion
        balise_passages = {}
        for aircraft in aircraft_list:
            estimated_times = aircraft.get_flight_plan_timed()
            for balise_name, passage_time in estimated_times.items():
                if balise_name not in balise_passages:
                    balise_passages[balise_name] = []
                balise_passages[balise_name].append((aircraft, passage_time))

        # Parcourir les balises et supprimer les conflits impliquant l'avion cible
        for balise_name, passages in balise_passages.items():
            if balise_name in self.balises: # Si balise deja en conflit 
                balise = self.balises[balise_name]
                for aircraft, _ in passages: # on parcours les avions qui la parcours
                    if aircraft.get_id_aircraft() != target_aircraft.get_id_aircraft(): # Si l'avion en conflit n'est pas l'avion cible 
                        balise.clear_conflicts_between(
                            target_aircraft.get_id_aircraft(),
                            aircraft.get_id_aircraft()
                        )

            # Analyser les conflits pour chaque balise
            if self.balises.get(balise_name):

                # Trier les passages par temps
                passages.sort(key=lambda x: x[1])
                conflicts: List[ConflictInformation] = []

                # Vérifier les conflits
                for i in range(len(passages) - 1):
                    for j in range(i + 1, len(passages)):
                        aircraft1, time1 = passages[i]
                        aircraft2, time2 = passages[j]
                        if np.abs(time2 - time1) > self.time_threshold:
                            break  # Les avions suivants sont trop éloignés dans le temps

                        #ajouter les conflit dans les balises et les trajectoires
                        else:
                            # conflicts.append({
                            #     "aircraft_1": aircraft1.get_id_aircraft(),
                            #     "speed_1": aircraft1.get_speed(),
                            #     "aircraft_2": aircraft2.get_id_aircraft(),
                            #     "speed_2": aircraft2.get_speed(),
                            #     "time_1": time1,
                            #     "time_2": time2,
                            #     "time_difference": time2 - time1,
                            # })
                            
                            conflict_info_one = ConflictInformation(aircraft1, aircraft2, time1, time2, self.balises.get(balise_name))
                            conflict_info_two = ConflictInformation(aircraft2, aircraft1, time2, time1, self.balises.get(balise_name))
                            
                            # Nettoyer les conflits entre 2 et 1
                            #aircraft2.clear_conflicts(with_aircraft_id=aircraft1.get_id_aircraft())

                            # Ajouter les conflits aux avions
                            aircraft1.set_conflicts(conflict_info_one)
                            #print(aircraft1.set_conflicts(conflict_info_one))
                            aircraft2.set_conflicts(conflict_info_two)
                            #print(aircraft2.set_conflicts(conflict_info_two))

                            conflicts.append(conflict_info_one)

                            if time1 < time2:
                                self.add_conflicts(conflict_info_one)
                                self.balises.get(balise_name).add_conflicts(conflict_info_one)
                            else:
                                self.add_conflicts(conflict_info_two)
                                self.balises.get(balise_name).add_conflicts(conflict_info_two)
                
                #if len(conflicts) > 0 :
                    #self.logger.info(f"Manager: conflicts detected for balise: {balise_name}")
                    #self.balises.get(balise_name).set_conflicts(conflicts)
        return None
    
    def add_conflicts(self, conflict: ConflictInformation) -> None:
        if not conflict in self.conflicts:
            self.conflicts.append(conflict)
    
    def delete_conflicts(self, conflict: ConflictInformation) -> None:
        try:
            self.conflicts.remove(conflict)
        except ValueError:
            pass
    
    def get_conflicts(self) -> List[ConflictInformation]:
        return list(sorted(self.conflicts, key=lambda c: c.get_conflict_time_one()))