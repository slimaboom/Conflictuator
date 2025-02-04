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
    def __init__(self, simulation_duration: time = time(hour=0, minute=30, second=0), 
                       lambda_poison: float = 0.0012, 
                       number_of_aircrafts: int = 15, 
                       **kwargs):
        """
        Initialise le générateur de trafic aérien.

        :param simulation_duration: Durée maximale de la simulation (en objet datetime.time).
        :param lambda_poisson: Paramètre lambda pour la loi de Poisson.
        """
        super().__init__(simulation_duration=simulation_duration, **kwargs)
        self.__lambda_poisson = lambda_poison
        self.__number_of_aircrafts = number_of_aircrafts
        self.routes = Airway.get_available_airways()
        self.route_rates = {}  # Stocke les paramètres lambda pour chaque route
        
        self.precision =  int(np.abs(np.floor(np.log10(abs(SpeedValue.MIN.value)))))

    def __fish_law_on_routes(self):
        """Calcule les taux de génération de trafic pour chaque route selon la loi de Poisson."""
        for route_key in self.routes:
            self.__set_poisson_rate(route_key, self.get_generator().uniform(self.__lambda_poisson, 1.5*self.__lambda_poisson))  # Exemple : lambda aléatoire entre 0.01 et 0.1 (0.0012)


    def __set_poisson_rate(self, route_key: str, rate: float):
        """
        Définit le taux de génération pour une route en ajustant par le nombre de routes partageant la même balise de départ.

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

    @override
    def generate_traffic(self) -> Dict[int, Aircraft]:
        """
        Génère le trafic aérien en fonction des lois de Poisson pour chaque route.

        :return: Dictionnaire d'objets Aircraft générés.
        """
        self.__fish_law_on_routes()

        data: Dict[int, Tuple] = {}
        for i, (route_key, rate) in enumerate(self.route_rates.items()):
            route = self.routes.get(route_key)
            if not route:
                continue

            # Points de la route transformés en balises
            flight_plan = route.get_transform_points()
            time = 0
            while time < self.get_simulation_duration():
                # Génère un intervalle suivant une loi de Poisson
                interval = np.random.poisson(1 / rate)
                time += interval
                if time > self.get_simulation_duration():
                    break

                # Crée un avion avec une vitesse aléatoire
                speed = self.get_generator().uniform(SpeedValue.MIN.value, SpeedValue.MAX.value) #SpeedValue.MIN.value, SpeedValue.MAX.value # Exemple d'intervalle de vitesse
                
                if len(data.values()) < self.__number_of_aircrafts:
                    data[i] = (round(speed, self.precision), flight_plan, time)
                else:
                    break
                
                #aircraft = Aircraft(speed=speed, flight_plan=flight_plan, take_off_time=time)
                #aircrafts[aircraft.get_id_aircraft()] = aircraft
        
        aircrafts = self.create_aircrafts(data)
        return aircrafts
    
    def create_aircrafts(self, data: Dict[int, Tuple]) -> Dict[int, Aircraft]:
        """Cree les avions a partir du dictionnaire de donnees qui contient le tuple: 
            speed, plan de vol, take off time
        """
        min_take_off_time = min([take_off_time for _, _, take_off_time in data.values()])
        aircrafts: Dict[int, Aircraft] = {}
        for tuple in data.values():
            speed, flight_plan, time = tuple

            # Décallage de l'avion vers le début de simulation
            take_off_time = time - min_take_off_time
            
            
            aircraft = Aircraft(speed=speed, flight_plan=flight_plan, take_off_time=take_off_time)
            aircrafts[aircraft.get_id_aircraft()] = aircraft
        
        last_times = max([a.get_arrival_time_on_last_point() for a in aircrafts.values()])
        self.set_simulation_duration(last_times)
        return aircrafts