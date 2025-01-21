import random
from model.aircraft import Aircraft
from generator.airways_generator import AirwaysGenerator

class TrafficGenerator:
    def __init__(self, airways_generator: AirwaysGenerator, interval: int = 120, max_aircraft: int = 10):
        """
        Initialise le générateur de trafic.
        :param airways_generator: Instance d'AirwaysGenerator pour assigner des routes.
        :param interval: Intervalle de temps entre les décollages (en secondes).
        :param max_aircraft: Nombre maximum d'avions par tranche de temps.
        :param sector: Instance de Sector définissant les limites géographiques du secteur.
        """
        self.airways_generator = airways_generator
        self.interval = interval
        self.max_aircraft = max_aircraft

    def generate_aircraft(self, start_time: float, duration: float):
        """
        Génère une liste d'avions pour une durée donnée.
        :param start_time: Heure de début de la simulation (en secondes).
        :param duration: Durée totale de la simulation (en secondes).
        :return: Liste d'instances d'Aircraft.
        """
        aircraft_list = []
        current_time = start_time

        while current_time < start_time + duration:
            num_aircraft = random.randint(1, self.max_aircraft)

            for _ in range(num_aircraft):
                # Utiliser AirwaysGenerator pour générer un plan de vol
                route = self.airways_generator.generate_route_between_different_quadrants()

                # Générer une vitesse réaliste
                speed = random.uniform(0.001, 0.0015)  # Vitesse normalisé

                # Créer une instance d'Aircraft
                aircraft = Aircraft(
                    speed=speed,
                    flight_plan=route
                )
                aircraft.set_take_off_time(current_time)
                aircraft_list.append(aircraft)

            # Avancer l'heure de l'intervalle défini
            current_time += self.interval

        return aircraft_list


