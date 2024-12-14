from dataclasses import dataclass
from typing import List, TYPE_CHECKING

from modele.balise import Balise
from modele.configuration import BALISES
from logging_config import setup_logging
if TYPE_CHECKING:
    from aircraft import Aircraft

@dataclass(frozen=True)
class ConflictInformation:
    aircraft_one: 'Aircraft'
    aircraft_two: 'Aircraft'
    conflict_time_one: float
    conflict_time_two: float
    location: Balise

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
        return f"Conflict(id_one={id_one}, id_two={id_two}, time_one={self.conflict_time_one}, time_two={self.conflict_time_two}, location=\'{self.location.get_name()}\')"


class ConflictManager:
    """Manager responsable de la détection et de la gestion des conflits."""
    logger = setup_logging("ConflictManager")

    def __init__(self, time_threshold: float = 60):
        self.aircraft_list = []
        self.balises = {}
        self.time_threshold = time_threshold

    def register_aircraft(self, aircraft: 'Aircraft') -> None:
        """Enregistre un avion dans le gestionnaire."""
        self.aircraft_list.append(aircraft)

    def register_balise(self, balise: Balise) -> None:
        """Enregistre une balise dans le gestionnaire."""
        self.balises[balise.get_name()] = balise

    def update_aircraft_conflicts(self, updated_aircraft: 'Aircraft') -> None:
        """
        Met à jour les conflits liés à un avion spécifique après un changement (ex: vitesse).
        """
        # Efface les anciens conflits de l'avion qui ont dépassé le temps courant
        self.logger.info(f"Start Mise a jour de l'avion:  {updated_aircraft.get_id_aircraft()}")

        # Recalcule les conflits impliquant cet avion
        self.detect_conflicts(self.aircraft_list)
        self.logger.info(f"End Mise a jour de l'avion:  {updated_aircraft.get_id_aircraft()}")


    def detect_conflicts(self, aircraft_list: List['Aircraft']) -> None:
        """
        Détecte les conflits de passage par les balises.
        Retourne un dictionnaire où chaque balise est associée à une liste de conflits.
        """
        self.logger.info(f"Calcul des conflits pour:  {[aircraft.get_id_aircraft() for aircraft in aircraft_list]}")

        # Collecter les temps de passage pour chaque avion
        balise_passages = {}
        for aircraft in aircraft_list:
            estimated_times = aircraft.get_flight_plan_timed()
            for balise_name, passage_time in estimated_times.items():
                if balise_name not in balise_passages:
                    balise_passages[balise_name] = []
                balise_passages[balise_name].append((aircraft, passage_time))

        # Analyser les conflits pour chaque balise
        for balise_name, passages in balise_passages.items():
            self.balises.get(balise_name).clear_conflicts() # Effacer les conflicts en cas de recalcul

            # Trier les passages par temps
            passages.sort(key=lambda x: x[1])
            conflicts = []

            # Vérifier les conflits
            for i in range(len(passages) - 1):
                aircraft1, time1 = passages[i]
                aircraft2, time2 = passages[i + 1]

                #ajouter les conflit dans les balises et les trajectoires
                if time2 - time1 <= self.time_threshold:
                    conflicts.append({
                        "aircraft_1": aircraft1.get_id_aircraft(),
                        "speed_1": aircraft1.get_speed(),
                        "aircraft_2": aircraft2.get_id_aircraft(),
                        "speed_2": aircraft2.get_speed(),
                        "time_1": time1,
                        "time_2": time2,
                        "time_difference": time2 - time1,
                    })
                    
                    conflict_info_one = ConflictInformation(aircraft1, aircraft2, time1, time2, self.balises.get(balise_name))
                    conflict_info_two = ConflictInformation(aircraft2, aircraft1, time2, time1, self.balises.get(balise_name))
                    
                    # Nettoyer les conflits entre 2 et 1
                    aircraft2.clear_conflicts(with_aircraft_id=aircraft1.get_id_aircraft())

                    # Ajouter les conflits aux avions
                    aircraft1.set_conflicts(conflict_info_one)
                    aircraft2.set_conflicts(conflict_info_two)
            
            if len(conflicts) > 0 :
                self.logger.info(f"Manager: conflicts detected for balise: {balise_name}")
                self.balises.get(balise_name).add_conflicts(conflicts)

        return None