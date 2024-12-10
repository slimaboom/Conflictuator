from modele.configuration import MAIN_SECTOR, SECONDARY_SECTOR, ROUTES, BALISES, AIRCRAFTS
from modele.aircraft import Aircraft
from modele.route import Airway
from modele.collector import Collector
from modele.sector import SectorName

from IHM.QtObject import QtSector, QtBalise, QtAirway, QtAircraft
from logging_config import setup_logging

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, Qt

from modele.conflict import Conflict

class SimulationController(QObject):
    INTERVAL = 100
    time_updated = pyqtSignal(float) # Signal qui transmet le temps écoulé (en seconds)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.aircrafts = None# Gestion d'un dictionnaire car recherche en O(1)
        self.sectors = None
        self.routes = None
        self.balises = None
        self.time_elapsed = 0
        self.running = False
        self.scene = scene

        self._interval = int(self.INTERVAL)
        self._speed_factor = 1
  
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

        self.initialize()

        # Logger pour logger et afficher des informations dans le terminal
        self.logger = setup_logging(__class__.__name__)


    def initialize(self) -> None:
        """Initialise les objets de simulation."""
        self.initialise_sectors()
        self.initialise_balises()
        self.initialise_routes()
        self.intialise_aircrafts()
        self.initialise_conflits()
        

    def initialise_sectors(self) -> None:
        sectors = [(SectorName.MAIN, MAIN_SECTOR), 
                        (SectorName.SECONDARY, SECONDARY_SECTOR)]
        
        self.sectors = Collector()
        # Dessiner les secteurs
        for sector_type, sector in sectors:
            if sector_type == SectorName.MAIN:
                qcolor=QColor("#D9EAD3")
            else:
                qcolor=QColor("#F3F3D9")

            for sector_name, points in sector.get_all().items():
                qtsector = QtSector(sector_name, parent=self.scene)
                qtsector.add_polygon(points, qcolor)
                # Sauvegarde du QtSector dans l'attribut sectors        
                self.sectors.add(sector_name, qtsector)

    def initialise_balises(self) -> None:
        self.balises = Collector()
        # Dessiner les balises
        qcolor = QColor("#BBBBBB")
        for balise_name, balise in BALISES.get_all().items():
            qtbalise = QtBalise(balise, parent=self.scene)
            qtbalise.makePolygon(qcolor)
            # Sauvegarde du QtBalise dans l'attribut balises
            self.balises.add(balise_name, qtbalise)
        

    def initialise_routes(self) -> None:
        self.routes = Collector()
        # Dessiner les routes aeriennes
        qcolor = QColor("lightGray")
        for airway_name, route in ROUTES.get_all().items():
            # Objet de representation en Qt
            qtairway = QtAirway(airway_name, parent=self.scene)
            # Conversion List[str] definissant la route en List[Balise]
            points = Airway.transform(route, BALISES, reverse=False)
            qtairway.add_path(points, qcolor)
            # Sauvegarde du QtAirway dans l'attribut routes
            self.routes.add(airway_name, qtairway)

    def intialise_aircrafts(self) -> None:
        self.aircrafts = Collector()
        # Dessiner les avions en mouvement
        for aircraft_id, aircraft in AIRCRAFTS.get_all().copy().items():
            qtaircraft = QtAircraft(aircraft.deepcopy(), parent=self.scene)

            # Sauvegarde du QtAIrcraft dans l'attribut aircraft
            self.aircrafts.add(aircraft_id, qtaircraft)
    
    def initialise_conflits(self) -> None:
        aircraft_list = []
        for aircraft in self.aircrafts.get_all().items(): 
            aircraft_list.append(aircraft[1].get_aircraft())
            Conflict.detect_conflicts(aircraft_list, 1000)

    def draw_sectors(self) -> None:
        # Ajouter les secteurs a la secene
        for _, qtsector in self.sectors.get_all().items():
            self.scene.addItem(qtsector)

    def draw_balises(self) -> None:
        # Ajouter les balises a la scene
        for _, qtbalise in self.balises.get_all().items():
            self.scene.addItem(qtbalise)

    def draw_airways(self) -> None:
        # Ajouter les routes aeriennes a la scene
        for _, qtairway in self.routes.get_all().items():
            self.scene.addItem(qtairway)
    
    def draw_aircrafts(self) -> None:
        # Ajouter les avions en mouvement a la scene
        for _, qtaircraft in self.aircrafts.get_all().items():
            self.scene.addItem(qtaircraft)


    def draw_boundary_rectangle(self) -> None:
        """Ajoute un rectangle pour délimiter la zone d'évolution des avions."""
        # Dimensions de la scène
        scene_width = self.scene.width()
        scene_height = self.scene.height()

        # Créer le rectangle
        rect = QGraphicsRectItem(0, 0, scene_width, scene_height)

        # Style des bordures
        pen = QPen(Qt.black)
        pen.setWidth(2)  # Épaisseur des bordures
        rect.setPen(pen)

        # Ajouter le rectangle à la scène
        self.scene.addItem(rect)

    def draw(self) -> None:
        # Dessiner la limite d'evoluation
        self.draw_boundary_rectangle()
        # Dessiner les secteurs
        self.draw_sectors()
        # Dessiner les routes aeriennes
        self.draw_airways()
        # Dessiner les balises
        self.draw_balises()
        # Dessiner les avions
        self.draw_aircrafts()


    def update_simulation(self) -> None:
        """Met à jour la simulation."""
        dt = self.timer.interval() # en milliseconds
        self.time_elapsed += dt * self._speed_factor
        self.time_updated.emit(self.time_elapsed/1000) # envoie du temps ecoulé

        for _, qtaircraft in self.aircrafts.get_all().items():
            qtaircraft.update(dt/1000, self._speed_factor) # Update QtAircraft et Aircraft
        
    def toggle_running(self) -> None:
        """Bascule entre démarrer/arrêter la simulation."""
        msg = f"Toggle running attribut from {self.running} to {not(self.running)}"
        
        self.running = not self.running
        if self.running:
            self.timer.start(self._interval) # Mettre a jour toutes les 100 ms
        else:
            self.timer.stop()
        self.logger.info(msg)

    def set_speed(self, speed_factor: int) -> None:
        """Modifie la vitesse de simulation."""
        self._speed_factor = int(speed_factor)
        self._interval = int(self.INTERVAL/(2*speed_factor))

    def stop_simulation(self):
        if self.running: self.toggle_running()

    def start_simulation(self):
        if not self.running: self.toggle_running()

    def get_aircrafts(self) -> Collector[QtAircraft]: return self.aircrafts
    def get_sectors(self) -> Collector[QtSector]: return self.sectors
    def get_routes(self) -> Collector[QtAirway]: return self.routes
    def get_balises(self) -> Collector[QtBalise]: return self.balises
    def get_time_elapsed(self) -> float: return self.time_elapsed / 1000
    def get_running(self) -> bool: return self.running

    def add_aircraft(self, aircraft: Aircraft) -> None:
        self.aircrafts.add(key=aircraft.get_id_aircraft(), value=aircraft)
        self.scene.parent()