import random
import numpy as np
from model.route import Airway
from model.balise import Balise
from model.aircraft.aircraft import Aircraft, AircraftCollector
from typing import List

class PTrafficGenerator:
    def __init__(self, max_duration: int):
        """
        Initialise le générateur de trafic aérien.

        :param routes: Les routes aériennes disponibles.
        :param balises: Les balises associées.
        :param max_duration: Durée maximale de la simulation (en secondes ou minutes).
        """
        self.routes = Airway.get_available_airways()
        self.max_duration = max_duration
        self.route_rates = {}  # Stocke les paramètres lambda pour chaque route

    def set_poisson_rate(self, route_key: str, rate: float):
        """
        Définit le taux de génération pour une route en ajustant par le nombre de routes avec la même balise de départ.

        :param route_key: Clé de la route.
        :param rate: Paramètre lambda pour la loi de Poisson.
        """
        route = self.routes.get(route_key)
        if not route:
            return

        # Identifier la balise de départ
        start_balise = route.get_start_balise_name()

        # Compter les routes partageant la même balise de départ
        shared_routes = [key for key in self.routes if self.routes.get(key) and self.routes.get(key).get_start_balise_name() == start_balise]
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
            route = self.routes.get(route_key)
            if not route:
                continue

            # Points de la route transformés en balises
            flight_plan = route.get_transform_points()
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
