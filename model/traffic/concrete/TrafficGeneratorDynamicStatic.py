from model.aircraft.aircraft import Aircraft
from model.route import Airway
from model.traffic.abstract.ATrafficGeneratorDynamic import ATrafficGeneratorDynamic
from utils.conversion import time_to_sec

from typing import Dict
from datetime import time
from typing_extensions import override

@ATrafficGeneratorDynamic.register_traffic_generator
class TrafficGeneratorDynamicStatic(ATrafficGeneratorDynamic):
    def __init__(self, simulation_duration: time = time(hour=0, minute=20, second=0), **kwargs):
        """
        Initialise le générateur de trafic aérien avec un nombre d'avion fixé et vitesse fixe
        :param simulation_duration: Durée maximale de la simulation (en objet datetime.time).
        """
        super().__init__(simulation_duration=simulation_duration, **kwargs)

    @override
    def generate_traffic(self) -> Dict[int, Aircraft]:
        """
        Génère le trafic aérien en fonction des lois de Poisson pour chaque route.

        :return: Dictionnaire d'objets Aircraft générés.
        """
        """aircrafts_list = [
                    Aircraft(speed=0.003, #0.001 # Conflit 5:48
                            flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI", "SICIL", "SODRI"])
                            ),

                    Aircraft(speed=0.002, 
                            flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "GAI"], reverse=True),
                            take_off_time=20),

                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"])),
                    
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "ETAMO"]))
        ]"""

        aircrafts_list = [
                    Aircraft(speed=0.003, #0.001 # Conflit 5:48
                            flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI", "SICIL", "SODRI"])
                            ),

                    Aircraft(speed=0.002, 
                            flight_plan=Airway.transform(["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"], reverse=True),
                            take_off_time=20),

                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["DIRMO", "ETAMO", "CFA", "MEN", "ETORI"])),
                        
                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"])),
                    
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "VULCA", "BURGO", "VEYRI"])),

                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "ETAMO"], reverse=True)),
                
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["SODRI", "SICIL", "JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]))
        ]


        """aircrafts_list = [
                    Aircraft(speed=0.003, #0.001 # Conflit 5:48
                            flight_plan=Airway.transform(["DIRMO", "ETAMO", "CFA", "MEN", "LOBOS", "GAI"])
                            ),

                    Aircraft(speed=0.002, 
                            flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"]),
                            take_off_time=20),

                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "SAMOS"])),
                        
                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["VEYRI", "MELKA", "PAS", "LIMAN", "LSE", "MINDI", "LANZA", "MEN", "LOBOS", "GAI"])),
                    
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["VEYRI", "MELKA", "SEVET", "JUVEN"])),

                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["FRI", "MELKA", "SEVET", "JUVEN"])),
                
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["BIELA", "JUVEN", "BOSUA", "GRENA", "MTL", "SPIDY", "ETORI", "ONGHI", "GAI"])),

                    Aircraft(speed=0.003, #0.001 # Conflit 5:48
                            flight_plan=Airway.transform(["DIRMO", "ETAMO", "CFA", "MEN", "LOBOS", "GAI"])
                            ),

                    Aircraft(speed=0.002, 
                            flight_plan=Airway.transform(["MAJOR", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]),
                            take_off_time=20),

                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["SODRI", "SICIL", "JAMBI", "MTL", "MINDI", "CFA", "VULCA"])),
                        
                    Aircraft(speed=0.001, 
                            flight_plan=Airway.transform(["GAI", "GWENA", "DIRMO"])),
                    
                    Aircraft(speed=0.0012, 
                            flight_plan=Airway.transform(["GAI", "ONGHI", "ETORI", "SPIDY", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"])),

        ]"""

        aircrafts = {a.get_id_aircraft():a  for a in aircrafts_list}
        last_times = max([a.get_arrival_time_on_last_point() for a in aircrafts.values()])
        self.set_simulation_duration(last_times)
        return aircrafts
    
