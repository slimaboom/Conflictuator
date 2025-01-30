import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import random
from generator.traffic_generator import PTrafficGenerator
from model.aircraft.aircraft import AircraftCollector
from model.route import Airway

import model.configuration # declenche les enregistrements de tout

AIRCRAFTS = AircraftCollector()
max_duration = 3600  # Une heure de simulation

# Initialisation du générateur de trafic
traffic_generator = PTrafficGenerator(max_duration)

# Définition des taux de génération (lambda) pour toutes les routes
print(Airway.get_available_airways())
for route_key in Airway.get_available_airways():
    traffic_generator.set_poisson_rate(route_key, random.uniform(0.0012, 0.0012))  # Exemple : lambda aléatoire entre 0.01 et 0.1

# Génération du trafic
aircrafts = traffic_generator.generate_traffic()

# Affichage des avions générés
for aircraft in aircrafts:
    AIRCRAFTS.add_aircraft(aircraft)
    print(f"Avion généré: vitesse={aircraft.speed}, départ={aircraft.take_off_time}, route={aircraft.flight_plan}")
print("c'est fini avec : ", len(aircrafts))