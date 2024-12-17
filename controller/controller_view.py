from model.sector import SectorType
from view.simulation_notifier import SimulationModelNotifier
from view.QtObject import QtSector, QtBalise, QtAirway, QtAircraft

from logging_config import setup_logging

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, Qt, QThread, QCoreApplication

from functools import partial
from typing import Callable, List



class SimulationViewController(QObject):
    # Signal qui transmet le temps écoulé (en secondes)
    chronometer = pyqtSignal(float)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        # Logger pour logger et afficher des informations dans le terminal
        self.logger = setup_logging(__class__.__name__)

        self.scene = scene
        self.simulation = SimulationModelNotifier()

        # Timer
        self.timer = QTimer()
        self.simulation.set_timer(self.timer)
        self.simulation.signal.aircrafts_moved.connect(self.update_view, type=Qt.QueuedConnection)

        # Gestion/Sauvegarde des Vues
        self.qt_sectors: List[QtSector] = []
        self.qt_balises: List[QtBalise] = []
        self.qt_routes: List[QtAirway]  = []
        self.qt_aircrafts: List[QtAircraft] = []

        self.static_items_drawn = False
        self.initialise_view()


    def initialise_view(self) -> None:
        """Initialise les objets de simulation pour la vue."""
        self.initialise_sectors_view()
        self.initialise_balises_view()
        self.initialise_routes_view()
        self.initialise_aircrafts_view()
        

    def initialise_sectors_view(self) -> None:
        """Initialise la vue des secteurs"""
        for sector_type, sectors in self.simulation.get_sectors().items():
            if sector_type == SectorType.MAIN:
                qcolor=QColor("#D9EAD3")
            else:
                qcolor=QColor("#F3F3D9")

            # Enregister les secteurs
            for sector_name, points in sectors.items():
                qtsector = QtSector(sector_name, parent=self.scene)
                qtsector.add_polygon(points, qcolor)

                # Sauvegarde du QtSector dans l'attribut qt_sectors
                self.qt_sectors.append(qtsector)

    def initialise_balises_view(self) -> None:
        """Initialise la vue des balises"""
        # Enregister les balises
        qcolor = QColor("#BBBBBB")
        for _, balise in self.simulation.get_balises().items():
            qtbalise = QtBalise(balise, parent=self.scene)
            qtbalise.makePolygon(qcolor)
            # Sauvegarde du QtBalise dans l'attribut balises
            self.qt_balises.append(qtbalise)
        

    def initialise_routes_view(self) -> None:
        """Initialise la vue des routes"""
        # Enregister les routes aeriennes
        qcolor = QColor("lightGray")
        for airway_name, route in self.simulation.get_routes().items():
            # Objet de representation en Qt
            qtairway = QtAirway(airway_name, parent=self.scene)
            qtairway.add_path(route, qcolor)
            # Sauvegarde du QtAirway dans l'attribut routes
            self.qt_routes.append(qtairway)

    def initialise_aircrafts_view(self) -> None:
        """Initialise la vue des avions"""
        # Enregister les avions en mouvement
        for _, aircraft in self.simulation.get_aircrafts().items():
            qtaircraft = QtAircraft(aircraft, parent=self.scene)

            # Sauvegarde du QtAircraft dans l'attribut aircrafts
            self.qt_aircrafts.append(qtaircraft)
    
    def draw_sectors(self) -> None:
        """Ajouter les secteurs a la scene"""
        # Ajouter les secteurs a la scene
        if not self.static_items_drawn:
            for qtsector in self.qt_sectors:
                self.scene.addItem(qtsector)

    def draw_balises(self) -> None:
        """Ajouter les balises a la scene"""
        # Ajouter les balises a la scene
        if not self.static_items_drawn:
            for qtbalise in self.qt_balises:
                self.scene.addItem(qtbalise)

    def draw_airways(self) -> None:
        """Ajouter les routes a la scene"""
        # Ajouter les routes aeriennes a la scene
        if not self.static_items_drawn:
            for qtairway in self.qt_routes:
                self.scene.addItem(qtairway)
    
    def draw_aircrafts(self) -> None:
        """Ajouter les avions a la scene"""
        # Ajouter les avions en mouvement a la scene
        speed_factor = self.simulation.get_speed_factor()
        for qtaircraft in self.qt_aircrafts:
            self.scene.addItem(qtaircraft)

    def moving_aircrafts(self) -> None:
        """Redessiner les avions qui bougent"""
        speed_factor = self.simulation.get_speed_factor()
        for qtaircraft in self.qt_aircrafts:
            qtaircraft.draw_aircraft()
            qtaircraft.draw_history(speed_factor)

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
        """Redessiner les objets sur la scene"""
        self.scene.update()

        if not self.static_items_drawn:
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
            
            # Mettre le flag a vrai pour eviter de redessiner les items statics
            self.static_items_drawn = True  

         # Toujours mettre a jour de facon dynamique
        self.moving_aircrafts()


    def update_view(self) -> None:
        """Met à jour la simulation en terme d'IHM."""
        # Continue with the UI update logic
        self.draw()
        self.chronometer.emit(self.simulation.get_time_elapsed())


    def toggle_running(self) -> None:
        """Bascule entre démarrer/arrêter la simulation."""
        self.simulation.toggle_running()

    def set_simulation_speed(self, speed_factor: int) -> None:
        """Modifie la vitesse de simulation."""
        self.simulation.set_simulation_speed(int(speed_factor))

    def stop_simulation(self): self.simulation.stop_simulation()
    def start_simulation(self): self.simulation.start_simulation()

    def connect_to_qtaircrafts(self, callback: Callable[[QtAircraft], None]) -> None:
        """Connexion du callback a l'evenement clicked sur le signal"""
        for qtaircraft in self.qt_aircrafts:
            qtaircraft.signal.clicked.connect(lambda _, qtacft=qtaircraft: callback(qtacft))
    
    def connect_to_qtbalises(self, callback: Callable[[QtBalise], None]) -> None:
        """Connexion du callback a l'evenement clicked sur le signal"""
        for qtbalise in self.qt_balises:
            qtbalise.signal.clicked.connect(lambda _, qtbal=qtbalise: callback(qtbal))