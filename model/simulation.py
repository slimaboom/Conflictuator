from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
from model.configuration import MAIN_SECTOR, SECONDARY_SECTOR
from model.aircraft.aircraft import Aircraft
from model.route import Airway
from model.balise import Balise
from model.sector import SectorType
from model.timer import Timer
from model.conflict_manager import ConflictManager

from algorithm.manager import AlgorithmManager
from algorithm.interface.IAlgorithm import AAlgorithm
from logging_config import setup_logging

from PyQt5.QtCore import QTimer

from queue import Queue
from typing import Dict, List, Callable, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from model.point import Point
    from model.balise import Balise

class SimulationModel:
    """Classe responsable de la logique de la simulation."""    
    
    INTERVAL: int = 100 # Intervalle par défaut en millisecondes (100 ms)

    def __init__(self, traffic_generator: ATrafficGenerator = None):
        # Logger pour logger et afficher des informations dans le terminal
        self.logger = setup_logging(__class__.__name__)
        
        # Gestion d'un dictionnaire car recherche en O(1)
        self.sectors: Dict[SectorType, Dict[str, List['Point']]]  = {}
        self.balises: Dict[str, 'Balise']      = {}
        self.routes: Dict[str, List['Balise']] = {}
        self.aircrafts: Dict[int, Aircraft]  = traffic_generator.generate_traffic() if traffic_generator else {}
        self.__aircraft_to_algo: Dict[int, Aircraft]  = {}
        self.__traffic_generator = traffic_generator

        # Gestion de la simulation
        self.time_elapsed = 0 # En secondes
        self.timer     = Timer()
        self.set_timer(self.timer)

        self._external_timer = None  # Timer externe, par défaut None
        self._speed_factor = 1

        # Enregistrer le gestionnaire comme observateur
        self.conflict_manager = ConflictManager(time_threshold=60)
        self.conflict_manager.set_time_simulation(self.time_elapsed)
        Aircraft.register_observer(self.conflict_manager)

        # Initialize objets for simulation
        self.initialize()

        # Algorithm manager
        self._algorithm_manager = AlgorithmManager(simulation_duration=None)

    def set_traffic_generator(self, traffic_generator: ATrafficGenerator) -> None:
        """Set le generateur de traffic à la simulation sous certaine condition
           Le simulateur n'a pas de generateur de traffic
           et l'argument du setter est du type ATrafficGenerator
        """
        # Sinon il faut recalculer le self.aircrafts et refaire self.initialize()
        if traffic_generator != None: # Protection 
            # Mise a jour de l'attribut
            self.__traffic_generator = traffic_generator
            self.__traffic_generator.reset_seed()

            # Generation du traffic
            self.aircrafts = traffic_generator.generate_traffic()
            self.initialise_aircrafts()
            self.initialise_conflicts()

            self._algorithm_manager.set_simulation_duration(self.get_simulation_time())

    def get_simulation_time(self) -> float:
        return self.__traffic_generator.get_simulation_duration()

    def initialize(self) -> None:
        """Initialise les objets de simulation."""
        self.initialise_sectors()
        self.initialise_balises()
        self.initialise_routes()
        self.initialise_aircrafts()
        self.initialise_conflicts()


    def initialise_sectors(self) -> None:
        """Sectors initialisation"""
        sectors = [(SectorType.MAIN, MAIN_SECTOR), 
                    (SectorType.SECONDARY, SECONDARY_SECTOR)]
        for sector_type, sector in sectors:
            self.sectors[sector_type] = {}
            for sector_name, points in sector.get_all().items():
                self.add_sector(sector_type, sector_name, points)

    def initialise_balises(self) -> None:
        """Balise initialisation"""
        for _, balise in Balise.get_available_balises().items():
            self.add_balise(balise)
        
    def initialise_routes(self) -> None:
        """Route/Airway initialisation"""
        for airway_name, route in Airway.get_available_airways().items():
            self.add_route(airway_name, route.get_transform_points())

    def initialise_aircrafts(self) -> None:
        """Aircraft initialisation"""
        for aircraft in self.aircrafts.values():
            self.add_aircraft(aircraft, register_to_manager=True)
    
    def initialise_conflicts(self) -> None:
        """Conflict initialisation"""
        for aircraft in self.aircrafts.values():
            # Enregistrer les avions dans le manager
            self.conflict_manager.register_aircraft(aircraft)
        
        for balise in self.balises.values():
            # Enregistrer les balises dans le manager
            self.conflict_manager.register_balise(balise)

        for aircraft in self.aircrafts.values():
            # Declencher la creation des conflicts
            #aircraft.set_speed(aircraft.get_speed())
            aircraft.set_commands(aircraft.get_commands())

    def get_algorithm(self) -> 'AAlgorithm': return self._algorithm_manager.get_algorithm()

    def set_algorithm(self, aalgorithm: AAlgorithm, *args, **kwargs) -> None: 
        self._algorithm_manager.set_data(self.__aircraft_to_algo.values())
        self._algorithm_manager.create_algorithm(aalgorithm, *args, **kwargs)


    def get_aircrafts(self) -> Dict[int, Aircraft]: return self.aircrafts
    def get_sectors(self) -> Dict[SectorType, Dict[str, List['Point']]]: return self.sectors
    def get_routes(self) -> Dict[str, List['Balise']]: return self.routes
    def get_balises(self) -> Dict[str, 'Balise']: return self.balises

    def get_time_elapsed(self) -> float: return self.time_elapsed
    def get_speed_factor(self) -> int: return self._speed_factor

    def add_aircraft(self, aircraft: Aircraft, register_to_manager: bool = False) -> None:
        self.aircrafts[aircraft.get_id_aircraft()] = aircraft
        if register_to_manager:
            self.conflict_manager.register_aircraft(aircraft)
            self.__aircraft_to_algo[aircraft.get_id_aircraft()] = aircraft

    def delete_aircraft(self, aircraft: Aircraft) -> bool:
        aircraft_key = aircraft.get_id_aircraft()
        if self.aircrafts.get(aircraft_key):
            del self.aircrafts[aircraft_key]
            deletion_okay = self.conflict_manager.delete_aircraft(aircraft)
            Aircraft.remove_aircraft_from_registry(aircraft)
            return deletion_okay
        else: return False
    

    def add_balise(self, balise: 'Balise') -> None:
        self.balises[balise.get_name()] = balise
  
    def delete_balise(self, balise: 'Balise') -> bool:
        balise_key = balise.get_name()
        if self.balises.get(balise_key):
            del self.balises[balise_key]
            return True
        else: return False
    

    def add_route(self, name: str, points: List['Balise']) -> None:
        self.routes[name] = points
    
    def delete_route(self, name: str) -> bool:
        if self.routes.get(name):
            del self.routes[name]
            return True
        else: return False
    

    def add_sector(self, sector_type: SectorType, name: str, points: List['Point']) -> None:
        self.sectors[sector_type][name] = points
    
    def delete_sector(self, sector_type: SectorType, name: str) -> bool:
        if self.sectors.get(sector_type).get(name):
            del self.sectors[sector_type][name]
            return True
        else: return False
    
    
    def set_timer(self, timer: Callable) -> None:
        """
        Permet de définir un timer externe (comme un QTimer) si besoin.
        :param timer: Le timer à utiliser (peut être QTimer ou un autre Timer)
        """
        is_running = self.timer.isActive() if self.timer else False
        # Stopper la simulation si en cours
        if is_running:
            self.stop_simulation()

        # Garder une référence du timer externe
        self._external_timer = timer 

        # Assigner le nouveau timer
        self.timer = timer
        
        # Reconnecter la méthode run() du modèle au timer
        if isinstance(self.timer, QTimer):
             self.timer.timeout.connect(self.run)
        else:
            self.connect(self.run)
            
        if is_running:
            self.timer.start(self.INTERVAL)

    def stop_simulation(self) -> None:
        if self.is_running(): self.toggle_running()

    def start_simulation(self) -> None:
        if not (self.is_running()) and not self.is_finished(): self.toggle_running()
    
    def is_running(self) -> bool: return self.timer.isActive()


    def run(self) -> None:
        """Met à jour la simulation."""
        dt = self.get_interval_timer() # converti en secondes
        
        for _ in range(self._speed_factor):
            if not self.is_finished():
                self.time_elapsed += dt
                for aircraft in self.aircrafts.values():
                    #self.logger.info(f"Avancement pour {aircraft.get_id_aircraft()} de {dt} seconds (elapsed: {self.time_elapsed})")
                    aircraft.update(timestep=dt)

                # Mise a jour du temps de simulation dans le manager de conflict (necessaire pour filtrer)
                self.conflict_manager.set_time_simulation(self.time_elapsed)

    def run_fast_simulation(self, elasped: float) -> None:
        """Met a jour la simulation en fonction du temps précis et non d'une courte durée d'avancement"""
        self.time_elapsed = elasped
        self.conflict_manager.set_time_simulation(self.time_elapsed)
        dt = self.get_interval_timer()
        elasped_minus = elasped - dt # retirer le temps du timer car aircraft.update(dt) va incrémenter 
        for aircraft in self.aircrafts.values():
            # Préciser à l'avion à quelle heure il est
            aircraft.set_time(elasped_minus)
            # Incrément de sa position, cap et temps de vol
            aircraft.update(dt)


    def toggle_running(self) -> None:
        """Bascule entre démarrer/arrêter la simulation."""
        msg = f"Toggle running attribut from {self.is_running()} to {not(self.is_running())}"
        
        if not self.timer.isActive():
            if not self.is_finished():
                self.timer.start(self.INTERVAL) # Mettre a jour toutes les 100 ms
        else:
            self.timer.stop()
        self.logger.info(msg)

    def set_simulation_speed(self, speed_factor: int) -> None:
        """Modifie la vitesse de simulation."""
        self._speed_factor = int(speed_factor)

    def stop_simulation(self):
        if self.is_running(): self.toggle_running()

    def start_simulation(self):
        if not self.is_running(): self.toggle_running()

    def connect(self, callback: Callable) -> None:
        self.timer.connect(callback)
    
    def is_running(self) -> bool: 
        return self.timer.isActive() if self.timer else False

    def start_algorithm(self, queue: 'Queue') -> None:
        self._algorithm_manager.start_algorithm(queue)
    
    def stop_algorithm(self) -> None:
        self._algorithm_manager.stop_algorithm()
    
    def get_progress_algorithm(self) -> float:
        return self._algorithm_manager.progress_algorithm()

    def get_process_time_algorithm(self) -> Tuple[float, float]:
        return self._algorithm_manager.process_time_algorithm()

    def get_algorithm_manager(self) -> AlgorithmManager:
        return self._algorithm_manager

    def get_interval_timer(self) -> float:
        """Retourne l'interval de déclenchement du timer en (s)"""
        interval = self.timer.interval()
        interval = interval if interval else self.INTERVAL # si pas déclencher depuis IHM, mettre la valeur par default
        return interval/1000 # converti en secondes

    def is_finished(self) -> bool:
        """Renvoie True si tous les avions ont atteints leur destination finale"""
        return all(a.has_reached_final_point() for a in self.get_aircrafts().values())
    
    def calcul_number_of_conflicts(self):
        """Calcul le nombre total de conflits entre les avions de la simulation"""
        total_conflicts = 0
        nc = 0.
        for aircraft_id, aircraft in self.aircrafts.items():
            if aircraft_id > 0:
                aircraft_conflicts = aircraft.get_conflicts().get_all()
                for conflicts in aircraft_conflicts.values():
                    nc = len(conflicts)
                    total_conflicts += nc
        return (total_conflicts * 0.5)