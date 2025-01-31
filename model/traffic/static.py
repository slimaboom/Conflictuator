from model.aircraft.aircraft import Aircraft, AircraftCollector
from model.route import Airway

import model.configuration

AIRCRAFTS = AircraftCollector() # Gestion d'un dictionnaire car recherche en O(1)

AIRCRAFTS.add_aircraft(Aircraft(speed=0.003, #0.001 # Conflit 5:48
                                flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI", "SICIL", "SODRI"])
                                ))
AIRCRAFTS.add_aircraft(Aircraft(speed=0.002, 
                                flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "GAI"], reverse=True),
                                take_off_time=20)
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.001, 
                                flight_plan=Airway.transform(["JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"]))
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.0012, 
                                flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "ETAMO"]))
)