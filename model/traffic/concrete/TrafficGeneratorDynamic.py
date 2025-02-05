import numpy as np
from datetime import time
from model.route import Airway
from model.aircraft.aircraft import Aircraft
from model.aircraft.speed import SpeedValue
from typing import Dict, Tuple

from model.traffic.abstract.ATrafficGeneratorDynamic import ATrafficGeneratorDynamic
from utils.conversion import time_to_sec
from typing_extensions import override

@ATrafficGeneratorDynamic.register_traffic_generator
class FishLawRoutesTrafficGeneratorDynamic(ATrafficGeneratorDynamic):
    MIN_INTERVAL_BETWEEN_DEPARTURES = 120  # Temps minimum en secondes entre deux avions d'une même balise

    def __init__(self, simulation_duration: time = time(hour=0, minute=30, second=0), 
                       lambda_poisson: float = 0.0012, 
                       number_of_aircrafts: int = 15, 
                       **kwargs):
        """
        Initialise le générateur de trafic aérien.

        :param simulation_duration: Durée maximale de la simulation.
        :param lambda_poisson: Paramètre lambda pour la loi de Poisson.
        :param number_of_aircrafts: Nombre total d'avions à générer.
        """
        super().__init__(simulation_duration=simulation_duration, **kwargs)
        self.__lambda_poisson = lambda_poisson
        self.__number_of_aircrafts = number_of_aircrafts
        self.routes = Airway.get_available_airways()
        
        self.precision = int(np.abs(np.floor(np.log10(abs(SpeedValue.MIN.value)))))
        self.__possible_speed = np.round(np.linspace(SpeedValue.MIN.value, SpeedValue.MAX.value, 20), self.precision)

    @override
    def generate_traffic(self) -> Dict[int, Aircraft]:
        """
        Génère le trafic aérien avec des temps de départ ajustés pour respecter un intervalle minimal.

        :return: Dictionnaire des avions générés.
        """
        if not self.routes or self.__number_of_aircrafts <= 0:
            return {}

        # Stocke le dernier temps de départ pour chaque balise
        last_departure_times = {}

        # Liste des avions à générer
        aircraft_data = []

        for _ in range(self.__number_of_aircrafts):
            # Sélectionne une route au hasard
            route_key = np.random.choice(list(self.routes.keys()))
            route = self.routes[route_key]
            start_balise = route.get_start_balise_name()
            flight_plan = route.get_transform_points()

            # Génère un temps de départ suivant la loi de Poisson
            interval = np.random.poisson(1 / self.__lambda_poisson)
            proposed_time = last_departure_times.get(start_balise, 0) + max(interval, self.MIN_INTERVAL_BETWEEN_DEPARTURES)

            # Assure que le temps reste dans la durée de simulation
            if proposed_time > self.get_simulation_duration():
                break  

            # Sélectionne une vitesse aléatoire
            speed = np.random.choice(self.__possible_speed)

            # Stocke les données de l'avion
            aircraft_data.append((speed, flight_plan, proposed_time))
            last_departure_times[start_balise] = proposed_time  # Mise à jour du dernier départ

        return self.create_aircrafts(aircraft_data)

    def create_aircrafts(self, aircraft_data: list) -> Dict[int, Aircraft]:
        """Crée les avions à partir des données collectées."""
        if not aircraft_data:
            return {}

        min_take_off_time = min(t for _, _, t in aircraft_data)
        aircrafts = {}

        for i, (speed, flight_plan, take_off_time) in enumerate(aircraft_data):
            adjusted_time = take_off_time - min_take_off_time  # Décalage au début de simulation
            aircraft = Aircraft(speed=speed, flight_plan=flight_plan, take_off_time=adjusted_time)
            aircrafts[aircraft.get_id_aircraft()] = aircraft

        # Met à jour la durée de simulation
        last_arrival = max(a.get_arrival_time_on_last_point() for a in aircrafts.values())
        self.set_simulation_duration(last_arrival)

        return aircrafts
