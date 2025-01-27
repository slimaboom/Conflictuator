import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.formatter.AFormat import AFormat
from model.aircraft import Aircraft
from model.configuration import BALISES
from model.route import Airway
from algorithm.storage import DataStorage

# Découvre tous les writters dans le package utils.writter
AFormat.discover_formatters('utils.formatter')

formatter = AFormat.create_formatter('json')
aircraft  = Aircraft(speed=0.003, #0.001 # Conflit 5:48
                    flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI", "SICIL", "SODRI"], BALISES)
                    )

commands = [DataStorage(speed=0.003, id=1, time=177.88, heading=5.516356508438049), 
            DataStorage(speed=0.0012, id=1, time=254.86, heading=5.516356508438049), 
            DataStorage(speed=0.002, id=1, time=300.58, heading=5.516356508438049), 
            DataStorage(speed=0.002, id=1, time=361.04, heading=5.516356508438049), 
            DataStorage(speed=0.002, id=1, time=363.05, heading=5.516356508438049)]

aircraft.set_commands(commands)
aircraft.set_time(commands[0].time)

time = 177.88
step = 0.1
for _ in range(61):
    aircraft.set_time(time)
    aircraft.update(timestep=step)
    time += step
    
print(formatter.export(aircraft))
print(AFormat.get_available_formats())