import random
import numpy as np
from model.configuration import BALISES, ROUTES
from model.route import Airway
from model.balise import DatabaseBalise
from model.aircraft.aircraft import Aircraft, AircraftCollector
from typing import List

class PTrafficGenerator:
    def __init__(self, routes: Airway, balises: DatabaseBalise, max_duration: int):
        """
        Initialise le générateur de trafic aérien.

        :param routes: Les routes aériennes disponibles.
        :param balises: Les balises associées.
        :param max_duration: Durée maximale de la simulation (en secondes ou minutes).
        """
        self.routes = routes
        self.balises = balises
        self.max_duration = max_duration
        self.route_rates = {}  # Stocke les paramètres lambda pour chaque route

    def set_poisson_rate(self, route_key: str, rate: float):
        """
        Définit le taux de génération pour une route en ajustant par le nombre de routes avec la même balise de départ.

        :param route_key: Clé de la route.
        :param rate: Paramètre lambda pour la loi de Poisson.
        """
        route = self.routes.get_from_key(route_key)
        if not route:
            return

        # Identifier la balise de départ
        start_balise = route[0]

        # Compter les routes partageant la même balise de départ
        shared_routes = [key for key in self.routes if self.routes.get_from_key(key) and self.routes.get_from_key(key)[0] == start_balise]
        adjustment_factor = len(shared_routes)

        # Ajuster le taux lambda
        adjusted_rate = rate / adjustment_factor if adjustment_factor > 0 else rate
        self.route_rates[route_key] = adjusted_rate

    def generate_traffic(self) -> List[Aircraft]:
        """
        Génère le trafic aérien en fonction des lois de Poisson pour chaque route.

        :return: Liste d'objets Aircraft générés.
        """
        aircrafts = []
        for route_key, rate in self.route_rates.items():
            route = self.routes.get_from_key(route_key)
            if not route:
                continue

            # Points de la route transformés en balises
            flight_plan = Airway.transform(route, self.balises)
            time = 0
            while time < self.max_duration:
                # Génère un intervalle suivant une loi de Poisson
                interval = np.random.poisson(1 / rate)
                time += interval
                if time > self.max_duration:
                    break

                # Crée un avion avec une vitesse aléatoire
                speed = random.uniform(0.001, 0.0015)  # Exemple d'intervalle de vitesse
                aircraft = Aircraft(speed=speed, flight_plan=flight_plan, take_off_time=time)
                aircrafts.append(aircraft)

        return aircrafts

"""
# Chargement des routes et des balises
routes = ROUTES  # Objets Airway définis dans configuration.py
balises = BALISES  # Objets DatabaseBalise définis dans configuration.py
AIRCRAFTS = AircraftCollector()
max_duration = 3600  # Une heure de simulation

# Initialisation du générateur de trafic
traffic_generator = PTrafficGenerator(routes, balises, max_duration)

# Définition des taux de génération (lambda) pour toutes les routes
for route_key in routes:
    traffic_generator.set_poisson_rate(route_key, random.uniform(0.0012, 0.0012))  # Exemple : lambda aléatoire entre 0.01 et 0.1

# Génération du trafic
aircrafts = traffic_generator.generate_traffic()

# Affichage des avions générés
for aircraft in aircrafts:
    AIRCRAFTS.add_aircraft(aircraft)
    print(f"Avion généré: vitesse={aircraft.speed}, départ={aircraft.take_off_time}, route={aircraft.flight_plan}")
print("c'est fini avec : ", len(aircrafts))
"""

#------------------------------------------------------------------------------
#--------- Definition  des avions:  -------------------------------------------
#------------------------------------------------------------------------------
AIRCRAFTS = AircraftCollector() # Gestion d'un dictionnaire car recherche en O(1)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.003, #0.001 # Conflit 5:48
                                flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "LTP", "GRENA", "SANTO", "JAMBI", "SICIL", "SODRI"], BALISES)
                                ))
AIRCRAFTS.add_aircraft(Aircraft(speed=0.002, 
                                flight_plan=Airway.transform(["ATN", "BURGO", "BOJOL", "LSE", "MINDI", "LANZA", "MEN", "GAI"], BALISES, reverse=True),
                                take_off_time=20)
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.001, 
                                flight_plan=Airway.transform(["JAMBI", "MTL", "LTP", "MOZAO", "SEVET", "RAPID"], BALISES))
)
AIRCRAFTS.add_aircraft(Aircraft(speed=0.0012, 
                                flight_plan=Airway.transform(["MAJOR", "MTL", "MINDI", "CFA", "ETAMO"], BALISES))
)

from model.aircraft.storage import DataStorage
commands = {1:
              [DataStorage(speed=0.0014, id=1, time=163.69, heading=5.516356508438049), 
               DataStorage(speed=0.0012, id=1, time=165.11, heading=5.516356508438049)],

            2:[DataStorage(speed=0.0012, id=2, time=40.12, heading=2.8036144653662953), 
               DataStorage(speed=0.0014, id=2, time=76.11, heading=2.8036144653662953), 
               DataStorage(speed=0.0014, id=2, time=158.25, heading=2.8036144653662953),
               DataStorage(speed=0.001, id=2, time=256.7, heading=2.8036144653662953), 
               DataStorage(speed=0.0016, id=2, time=297.57, heading=2.8036144653662953)],

            3:[DataStorage(speed=0.001, id=3, time=40.94, heading=1.7053337239371453), 
               DataStorage(speed=0.001, id=3, time=139.13, heading=1.7053337239371453), 
               DataStorage(speed=0.0016, id=3, time=167.94, heading=1.7053337239371453), 
               DataStorage(speed=0.0014, id=3, time=202.31169820253618, heading=1.7053337239371453), 
               DataStorage(speed=0.0016, id=3, time=203.49, heading=1.7053337239371453)],


            4: [DataStorage(speed=0.0012, id=4, time=112.61, heading=6.014843526578622), 
                DataStorage(speed=0.0012, id=4, time=112.61, heading=6.014843526578622), 
                DataStorage(speed=0.0014, id=4, time=162.09369736286513, heading=6.014843526578622), 
                DataStorage(speed=0.0016, id=4, time=270.5777672165488, heading=6.014843526578622)]
            }

#for id, command in commands.items():
#    AIRCRAFTS.get_from_key(id).set_commands(commands=command)
