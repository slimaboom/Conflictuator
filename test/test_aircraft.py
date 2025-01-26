import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generator.traffic_generator import AIRCRAFTS
from logging_config import setup_logging
from model.utils import sec_to_time
from algorithm.storage import DataStorage

logger = setup_logging(__file__.split("/")[-1])

# Solution Genetique
commands_aircraft = {1:
                        [DataStorage(speed=0.003, id=1, time=177.88, heading=5.516356508438049), 
                         DataStorage(speed=0.0012, id=1, time=254.86, heading=5.516356508438049), 
                         DataStorage(speed=0.002, id=1, time=300.58, heading=5.516356508438049), 
                         DataStorage(speed=0.002, id=1, time=361.04, heading=5.516356508438049), 
                         DataStorage(speed=0.002, id=1, time=363.05, heading=5.516356508438049)],

                    2:[DataStorage(speed=0.001, id=2, time=86.82, heading=2.8036144653662953), 
                       DataStorage(speed=0.001, id=2, time=143.11007192969376, heading=2.8036144653662953), 
                       DataStorage(speed=0.0012, id=2, time=167.46311160769378, heading=2.8036144653662953), 
                       DataStorage(speed=0.003, id=2, time=196.75, heading=2.8036144653662953)],
                    
                    3:[DataStorage(speed=0.001, id=3, time=53.71, heading=1.7053337239371453), 
                       DataStorage(speed=0.002, id=3, time=82.47, heading=1.7053337239371453), 
                       DataStorage(speed=0.003, id=3, time=169.66009373296203, heading=1.7053337239371453), 
                       DataStorage(speed=0.003, id=3, time=269.65, heading=1.7053337239371453)],
                    
                    4:[DataStorage(speed=0.003, id=4, time=144.34, heading=6.014843526578622), 
                       DataStorage(speed=0.001, id=4, time=208.96, heading=6.014843526578622), 
                       DataStorage(speed=0.002, id=4, time=305.81, heading=6.014843526578622), 
                       DataStorage(speed=0.003, id=4, time=352.87, heading=6.014843526578622)]
}

for id, aircraft in AIRCRAFTS.get_all().items():
   cmds = commands_aircraft.get(id)

   aircraft.set_commands(cmds)
   aircraft.calculate_estimated_times_commands()

   fpt = aircraft.get_flight_plan_timed()
   fpt = {k: f"{v} ({sec_to_time(v)})" for k,v in fpt.items()}
   msg = f"\nAircraft Id: {id}\nFlightPlanTimed:\n{fpt}\n\n"

   logger.info(msg)