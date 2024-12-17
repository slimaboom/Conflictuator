from model.configuration import MAIN_SECTOR, SECONDARY_SECTOR, ROUTES, BALISES, AIRCRAFTS
from model.aircraft import Aircraft
from model.route import Airway
from model.sector import SectorType
from model.timer import Timer
from model.conflict_manager import ConflictManager

from logging_config import setup_logging

from threading import Thread
from queue import Queue
from PyQt5.QtCore import QTimer

from typing import Dict, List, Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from model.point import Point
    from model.balise import Balise

class SimulationModel:
    """Classe responsable de la logique de la simulation."""    
    
    INTERVAL: int = 100 # Intervalle par défaut en millisecondes (100 ms)

    def __init__(self):
        # Logger pour logger et afficher des informations dans le terminal
        self.logger = setup_logging(__class__.__name__)
        
        # Gestion d'un dictionnaire car recherche en O(1)
        self.sectors: Dict[SectorType, Dict[str, List['Point']]]  = {}
        self.balises: Dict[str, 'Balise']      = {}
        self.routes: Dict[str, List['Balise']] = {}
        self.aircrafts: Dict[int, Aircraft]  = {}

        # Gestion de la simulation
        self.time_elapsed = 0 # En secondes
        self.timer     = Timer()
        self._external_timer = None  # Timer externe, par défaut None
        self._speed_factor = 1


        # Enregistrer le gestionnaire comme observateur
        self.conflict_manager = ConflictManager(time_threshold=60)
        self.conflict_manager.set_time_simulation(self.time_elapsed)
        Aircraft.register_observer(self.conflict_manager)

        # Initialize objets for simulation
        self.initialize()

        # Algorithm used ? Recuit/Genetique
        self._algorithm = None


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
        for balise in BALISES.get_all().copy().values():
            self.add_balise(balise.deepcopy())
        
    def initialise_routes(self) -> None:
        """Route/Airway initialisation"""
        for airway_name, route in ROUTES.get_all().items():
            self.add_route(airway_name, route)

    def initialise_aircrafts(self) -> None:
        """Aircraft initialisation"""
        for aircraft in AIRCRAFTS.get_all().copy().values():
            self.add_aircraft(aircraft.deepcopy())
    
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
            aircraft.set_speed(aircraft.get_speed())

    def get_algorithm(self): return self._algorithm
    def set_algorithm(self, algo) -> None: self._algorithm = algo

    def get_aircrafts(self) -> Dict[int, Aircraft]: return self.aircrafts
    def get_sectors(self) -> Dict[SectorType, Dict[str, List['Point']]]: return self.sectors
    def get_routes(self) -> Dict[str, List['Balise']]: return self.routes
    def get_balises(self) -> Dict[str, 'Balise']: return self.balises

    def get_time_elapsed(self) -> float: return self.time_elapsed
    def get_running(self) -> bool: return self.running
    def get_speed_factor(self) -> int: return self._speed_factor

    def add_aircraft(self, aircraft: Aircraft) -> None:
        self.aircrafts[aircraft.get_id_aircraft()] = aircraft

    def delete_aircraft(self, aircraft: Aircraft) -> bool:
        aircraft_key = aircraft.get_id_aircraft()
        if self.aircrafts.get(aircraft_key):
            del self.aircrafts[aircraft_key]
            return True
        else: return False
    

    def add_balise(self, balise: 'Balise') -> None:
        self.balises[balise.get_name()] = balise
  
    def delete_balise(self, balise: 'Balise') -> bool:
        balise_key = balise.get_name()
        if self.balises.get(balise_key):
            del self.balises[balise_key]
            return True
        else: return False
    

    def add_route(self, name: str, points: List[str]) -> None:
        route_balises = Airway.transform(points, BALISES, reverse=False)
        self.routes[name] = route_balises
    
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
        if self.timer.isActive(): self.toggle_running()

    def start_simulation(self) -> None:
        if not self.timer.isActive(): self.toggle_running()
    
    def is_running(self) -> bool: return self.timer.isActive()


    def run(self) -> None:
        """Met à jour la simulation."""

        dt = self.timer.interval()/1000 # converti en secondes
        
        for _ in range(self._speed_factor):
            self.time_elapsed += dt
            for aircraft in self.aircrafts.values():
                if aircraft.get_take_off_time() <= self.time_elapsed: # Decollage
                    aircraft.update(timestep=dt)

        # Mise a jour du temps de simulation dans le manager de conflict (necessaire pour filtrer)
        self.conflict_manager.set_time_simulation(self.time_elapsed)


    def toggle_running(self) -> None:
        """Bascule entre démarrer/arrêter la simulation."""
        msg = f"Toggle running attribut from {self.is_running()} to {not(self.is_running())}"
        
        if not self.timer.isActive():
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

    def run_algorithm(self) -> Any:
        """
        Lance l'algorithme (par exemple recuit simulé) dans un thread séparé
        et récupère les résultats via une Queue.
        """
        if self._algorithm:
            # Créer une Queue pour récupérer les résultats
            result_queue = Queue()

            # Créer un thread pour exécuter l'algorithme
            thread = Thread(target=self._run_algorithm_in_thread, args=(result_queue,), daemon=True)
            thread.start()

            # Attendre que le thread ait terminé et récupérer le résultat
            result = result_queue.get()  # Récupère le résultat de la Queue
            return result

    def _run_algorithm_in_thread(self, result_queue: Queue) -> None:
        """
        Méthode interne qui exécute l'algorithme dans un thread séparé.
        Elle place les résultats dans la Queue.
        """
        if self._algorithm:
            # Exécute l'algorithme (par exemple recuit simulé)
            result = self._algorithm.run()  # Exécution de l'algorithme

            # Une fois l'algorithme terminé, on met les résultats dans la Queue
            result_queue.put(result)