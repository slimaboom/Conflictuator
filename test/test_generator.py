import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from model.traffic.concrete.TrafficGeneratorDynamic import TrafficGeneratorDynamic
from model.route import Airway

import model.configuration # declenche les enregistrements de tout

max_duration = 3600  # Une heure de simulation

# Initialisation du générateur de trafic
traffic_generator = TrafficGeneratorDynamic(max_duration, lambda_poison=0.0012)

# Définition des taux de génération (lambda) pour toutes les routes
print(Airway.get_available_airways())

# Génération du trafic
aircrafts = traffic_generator.generate_traffic()

# Affichage des avions générés
for aircraft in aircrafts.values():
    print(f"Avion généré: vitesse={aircraft.get_speed()}, départ={aircraft.get_take_off_time()}, route={aircraft.get_flight_plan()}")
print("c'est fini avec : ", len(aircrafts))