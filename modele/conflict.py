from dataclasses import dataclass
from typing import List, Dict, TYPE_CHECKING
from modele.configuration import BALISES, AIRCRAFTS
from modele.utils import sec_to_time

if TYPE_CHECKING:
    from modele.aircraft import Aircraft

@dataclass(frozen=True)
class Conflict:
    aircraft_one: 'Aircraft'
    aircraft_two: 'Aircraft'
    conflict_time_one: float
    conflict_time_two: float
    location: str # Balise.get_name...

    @property
    def time_difference(self) -> float:
        """Calcule la différence de temps entre les deux avions."""
        return self.conflict_time_two - self.conflict_time_one

    def get_aircraft_one(self): return self.aircraft_one
    def get_aircraft_two(self): return self.aircraft_two

    def get_conflict_time_one(self): return self.conflict_time_one
    def get_conflict_time_two(self): return self.conflict_time_two
    
    def get_location(self): return self.location
    def get_time_difference(self): return self.time_difference
    
    def __repr__(self):
        id_one = self.aircraft_one.get_id_aircraft()
        id_two = self.aircraft_two.get_id_aircraft()
        return f"Conflict(id_one={id_one}, id_two={id_two}, time_one={self.conflict_time_one}, time_two={self.conflict_time_two}, location=\'{self.location}\')"

    @staticmethod
    def detect_conflicts(aircraft_list: List['Aircraft'], time_threshold: float = 60) -> None: # La fonction ne renvoie rien
        """
        Détecte les conflits de passage par les balises.
        Retourne un dictionnaire où chaque balise est associée à une liste de conflits.
        """

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
            # Trier les passages par temps
            passages.sort(key=lambda x: x[1])
            conflicts = []

            # Vérifier les conflits
            for i in range(len(passages) - 1):
                aircraft1, time1 = passages[i]
                aircraft2, time2 = passages[i + 1]

                #ajouter les conflit dans les balises et les trajectoires
                if time2 - time1 <= time_threshold:
                    conflicts.append({
                        "aircraft_1": aircraft1.get_id_aircraft(),
                        "speed_1": aircraft1.get_speed(),
                        "aircraft_2": aircraft2.get_id_aircraft(),
                        "speed_2": aircraft2.get_speed(),
                        "time_1": time1,
                        "time_2": time2,
                        "time_difference": time2 - time1,
                    })
                    
                    conflict_info_one = Conflict(aircraft1, aircraft2, time1, time2, balise_name)
                    conflict_info_two = Conflict(aircraft2, aircraft1, time2, time1, balise_name)
                    # Ajouter les conflits aux avions
                    aircraft1.set_conflicts(conflict_info_one)
                    aircraft2.set_conflicts(conflict_info_two)
            
            if len(conflicts) > 0 :
                BALISES.get_from_key(balise_name).add_conflicts(conflicts)

        return None
    
    @staticmethod
    def set_conflict_text(conflict: Dict[str, float], text1: str) -> str:
        
        aircraft_id1 = conflict["aircraft_1"]
        aircraft_1 = AIRCRAFTS.get_from_key(aircraft_id1)
        aircraft_id2 = conflict["aircraft_2"]
        aircraft_2 = AIRCRAFTS.get_from_key(aircraft_id2)
        conflict_time = conflict["time_1"]
        text = text1
        v1 = f"{aircraft_1.get_speed():.1e}".replace('.0', '')
        v2 = f"{aircraft_2.get_speed():.1e}".replace('.0', '')
        # Ajout du style CSS pour décaler légèrement le texte vers la gauche
        text += """
        <style>
            .conflict {
                margin-left: -10px;  /* Décale légèrement le contenu à gauche */
            }
        </style>
        <div class="conflict">
        """
        text += f"""
            <b> Time : </b> {sec_to_time(conflict_time)}<br>({conflict_time} s)<br>
            <li>
                <b>Avion 1 :</b> {aircraft_id1}<br>
                <b>Position :</b> ({aircraft_1.get_position().getX():.2f}, 
                                    {aircraft_1.get_position().getY():.2f})<br>
                <b>Vitesse :</b> {v1} unité/s<br>
                    <b>Cap :</b> {aircraft_1.get_heading(in_aero=True):.2f}°<br>
                    <br>
                    <b>Avion 2 :</b> {aircraft_id2}<br>
                    <b>Position :</b> ({aircraft_2.get_position().getX():.2f}, 
                                        {aircraft_2.get_position().getY():.2f})<br>
                    <b>Vitesse :</b> {v2} unité/s<br>
                    <b>Cap :</b> {aircraft_2.get_heading(in_aero=True):.2f}°<br>
                    <br>
                </li>
        """
        text += "</div></ul>"
        return text


