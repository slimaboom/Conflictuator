from model.sector import SectorType
from view.simulation_notifier import SimulationModelNotifier
from view.QtObject import QtSector, QtBalise, QtAirway, QtAircraft

from logging_config import setup_logging

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, Qt

from typing import Callable, List, TYPE_CHECKING, Dict
from copy import deepcopy

if TYPE_CHECKING:
    from algorithm.type import AlgoType
    from queue import Queue



class SimulationViewController(QObject):
    # Signal qui transmet le temps écoulé (en secondes)
    chronometer = pyqtSignal(float)
    algorithm_terminated = pyqtSignal()
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        # Logger pour logger et afficher des informations dans le terminal
        self.logger = setup_logging(__class__.__name__)

        self.scene = scene
        self.simulation = SimulationModelNotifier()

        # Timer
        self.timer = QTimer()
        self.simulation.set_timer(self.timer)
        self.simulation.signal.aircrafts_moved.connect(self.update_view, type=Qt.QueuedConnection)  # Assure que le signal est traité dans le thread principal
        self.aircraft_click_callback = None  # Callback pour les clics

        # Gestion/Sauvegarde des Vues
        self.qt_sectors: List[QtSector] = []
        self.qt_balises: List[QtBalise] = []
        self.qt_routes: List[QtAirway]  = []
        self.qt_aircrafts: Dict[int, QtAircraft] = {}
        self.static_items_drawn = False

        self.initialise_view()

        # Algorithme results
        self.simulation.signal.algorithm_terminated.connect(self.update_view_with_algorithm, type=Qt.QueuedConnection)  # Assure que le signal est traité dans le thread principal
        self.logger.info(self.qt_aircrafts)


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
            qtaircraft = QtAircraft(aircraft, parent=self.scene, qcolor=Qt.green)
            
            # Sauvegarde du QtAircraft dans l'attribut aircrafts
            self.qt_aircrafts[aircraft.get_id_aircraft()] = qtaircraft
    
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
        for qtaircraft in self.qt_aircrafts.values():
            self.logger.info(f"{qtaircraft} added in the scene")
            self.scene.addItem(qtaircraft)

    def moving_aircrafts(self) -> None:
        """Redessiner les avions qui bougent"""
        speed_factor = self.simulation.get_speed_factor()
        for qtaircraft in self.qt_aircrafts.values():
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
            self.logger.info("draw method call")
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
        self.aircraft_click_callback = callback  # Callback pour les clics
        for qtaircraft in self.qt_aircrafts.values():
            qtaircraft.signal.clicked.connect(lambda _, qtacft=qtaircraft: callback(qtacft))
            qtaircraft.setAcceptHoverEvents(True)

    def connect_to_qtbalises(self, callback: Callable[[QtBalise], None]) -> None:
        """Connexion du callback a l'evenement clicked sur le signal"""
        for qtbalise in self.qt_balises:
            qtbalise.signal.clicked.connect(lambda _, qtbal=qtbalise: callback(qtbal))
    
    def disable_aircraft_interactions(self) -> None:
        """Désactive les clics utilisateur sur les avions."""
        for qtaircraft in self.qt_aircrafts.values():
            try:
                # Déconnecter le signal
                qtaircraft.signal.clicked.disconnect()
                self.logger.info(f"disable connexion of {qtaircraft}")
            except TypeError:
                # Si déjà déconnecté, ignorer l'erreur
                self.logger.info(f"Echec disable connexion of {qtaircraft}")
                pass

    def enable_original_aircraft_interactions(self) -> None:
        """Réactive les clics uniquement pour les avions originaux."""
        if self.aircraft_click_callback:
            self.connect_to_qtaircrafts(self.aircraft_click_callback)

    def start_algorithm(self, algotype: 'AlgoType') -> None:
        self.simulation.start_algorithm(algotype)
    
    def copy_qtaircrafts(self) -> List[QtAircraft]:
        new_qtaircrafts = []
        for qtaircraft in self.qt_aircrafts.values():
            aircraft = qtaircraft.get_aircraft().deepcopy()
            aircraft.set_aircraft_id(-aircraft.get_id_aircraft())

            qt_aircraft = QtAircraft(aircraft, parent=self.scene, qcolor=Qt.gray)
            new_qtaircrafts.append(qt_aircraft)

        self.logger.info(new_qtaircrafts)
        return new_qtaircrafts

    def update_view_with_algorithm(self, queue: 'Queue'):
        self.logger.info(queue)
        final = queue.get_nowait()
        
        qt_aircrafts_copies = self.copy_qtaircrafts()

        # Mise à jour des avions optimaux
        for datastorage in final:
            id, speed = datastorage.id, datastorage.speed
            
            qtaircraft = self.qt_aircrafts.get(id)
            aircraft = qtaircraft.get_aircraft()

            # Vérifier si l'avion est déjà dans la scène
            if qtaircraft not in self.scene.items():
                self.logger.warning(f"Avion manquant dans la scène : {aircraft.get_id_aircraft()} (recréation possible)")
                self.scene.addItem(qtaircraft)

            # Mettre à jour les paramètres de l'avion
            aircraft.set_speed(speed)
            self.logger.info(f"Avion {aircraft.get_id_aircraft()} mis à jour, vitesse : {speed}")

            # Assurer un Z-index élevé pour les avions originaux
            qtaircraft.setZValue(2)
        
        self.enable_original_aircraft_interactions()

        # Ajouter les copies des avions (optimaux) à la scène
        for qtaircraft_copy in qt_aircrafts_copies:
            # Rendre les copies distinctes visuellement
            qtaircraft_copy.setOpacity(0.4)
            qtaircraft_copy.setZValue(1)  # Z-index inférieur pour apparaître sous les originaux
            self.logger.info(f"Add {qtaircraft_copy} to dictionnary")


            # Ajouter à la scène et les listes internes
            self.qt_aircrafts[qtaircraft_copy.get_aircraft().get_id_aircraft()] = qtaircraft_copy
            self.simulation.add_aircraft(qtaircraft_copy.get_aircraft(), register_to_manager=False)
            
            self.scene.addItem(qtaircraft_copy)

        self.logger.info(self.qt_aircrafts)

        # Emission du signal de terminaison
        self.algorithm_terminated.emit()

    def cleanup(self) -> None:
        self.logger.info("Nettoyage des objets de l'ancienne vue...")
        self.disable_aircraft_interactions()
        
        # Supprimer les avions de la scène
        for qtaircraft in list(self.qt_aircrafts.values()):
            if qtaircraft in self.scene.items():
                self.scene.removeItem(qtaircraft)

        # Nettoyer les listes internes
        self.qt_aircrafts.clear()
        self.qt_sectors.clear()
        self.qt_balises.clear()
        self.qt_routes.clear()
        
        # Déconnecter les signaux pour éviter les callbacks
        self.simulation.signal.aircrafts_moved.disconnect(self.update_view)
        self.simulation.signal.algorithm_terminated.disconnect(self.update_view_with_algorithm)
