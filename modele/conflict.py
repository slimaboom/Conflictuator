from dataclasses import dataclass
from typing import List, Dict
from modele.configuration import MAIN_SECTOR, SECONDARY_SECTOR, BALISES, ROUTES, AIRCRAFTS
from modele.aircraft import Aircraft
from logging_config import setup_logging
@dataclass
class Conflict:

    def __init__(self):
        self.logger  = setup_logging(__class__.__name__)
    
    def detect_conflicts(aircraft_list: List[Aircraft], time_threshold: float = 60) -> Dict[str, List[Dict]]:
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
            
            if len(conflicts) > 0 :
                BALISES.get_from_key(balise_name).add_conflicts(conflicts)


        return None
    
    def set_conflict_text(conflict, text1):
        
        aircraft_id1 = conflict["aircraft_1"]
        aircraft_1 = AIRCRAFTS.get_from_key(aircraft_id1)
        aircraft_id2 = conflict["aircraft_2"]
        aircraft_2 = AIRCRAFTS.get_from_key(aircraft_id2)
        time_to_conflict = ""
        text = text1
        text += f"""
            <b> Time : </b> {conflict["time_1"]}<br>
            <li>
                <b>Avion 1 :</b> {aircraft_id1}<br>
                <b>Position :</b> ({aircraft_1.get_position().getX():.2f}, 
                                    {aircraft_1.get_position().getY():.2f})<br>
                <b>Vitesse :</b> {aircraft_1.get_speed():.2f} unités<br>
                <b>Cap :</b> {aircraft_1.get_heading(in_aero=True):.2f}°<br>
                <br>
                <b>Avion 2 :</b> {aircraft_id2}<br>
                <b>Position :</b> ({aircraft_2.get_position().getX():.2f}, 
                                    {aircraft_2.get_position().getY():.2f})<br>
                <b>Vitesse :</b> {aircraft_2.get_speed():.2f} unités<br>
                <b>Cap :</b> {aircraft_2.get_heading(in_aero=True):.2f}°<br>
                <br>
                
            </li>
            """
        text += "</ul>"
        return text


