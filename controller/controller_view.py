from model.sector import SectorType
from model.traffic.abstract import ATrafficGenerator
from view.simulation_notifier import SimulationModelNotifier
from view.QtObject import QtSector, QtBalise, QtAirway, QtAircraft
from view.arrival_manager import ArrivalManagerWindow
from utils.formatter.AFormat import AFormat
from utils.writer.AWriter import AWriter

from algorithm.interface.IAlgorithm import AAlgorithm

from logging_config import setup_logging

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import QTimer, QObject, pyqtSignal, Qt

from typing import Callable, List, Dict
from threading import Thread
from queue import Queue



class SimulationViewController(QObject):
    # Signal qui transmet le temps écoulé (en secondes)
    chronometer = pyqtSignal(float)
    algorithm_terminated = pyqtSignal(object)
    recording_terminated = pyqtSignal(bool)
    
    ___THREADS: List[Thread] = []

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
        #self.logger.info(self.qt_aircrafts)

    def set_traffic_generator(self, traffic_generator: ATrafficGenerator) -> None:
        """Set le generateur de traffic au controleur"""
        self.simulation.set_traffic_generator(traffic_generator=traffic_generator)
        self.initialise_view() # reinitialisation de la vue
        self.draw()


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
            self.logger.info(f"{aircraft.get_id_aircraft()}, {aircraft.get_conflicts().get_all()}")
        
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
            #self.logger.info(f"{qtaircraft} added in the scene")
            self.scene.addItem(qtaircraft)

    def moving_aircrafts(self) -> None:
        """Redessiner les avions qui bougent"""
        speed_factor = self.simulation.get_speed_factor()
        for qtaircraft in self.qt_aircrafts.values():
            if qtaircraft.get_aircraft().get_take_off_time() <= self.simulation.get_time_elapsed():
                if not qtaircraft.isVisible():
                    qtaircraft.setVisible(True)

                qtaircraft.draw_aircraft()
                qtaircraft.draw_history(speed_factor)
            else:
                qtaircraft.setVisible(False)

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
        self.update_qt_balises_color()



    def update_view(self) -> None:
        """Met à jour la simulation en terme d'IHM."""
        # Continue with the UI update logic
        self.draw()
        self.chronometer.emit(self.simulation.get_time_elapsed())
        self.simulation.is_finished()


    def toggle_running(self) -> None:
        """Bascule entre démarrer/arrêter la simulation."""
        self.simulation.toggle_running()

    def set_simulation_speed(self, speed_factor: int) -> None:
        """Modifie la vitesse de simulation."""
        self.simulation.set_simulation_speed(int(speed_factor))

    def stop_simulation(self): self.simulation.stop_simulation()
    def start_simulation(self): self.simulation.start_simulation()

    def run_fast_simulation(self, elasped: float) -> None:
        """Permet d'exécute la méthode du modèle logique. C'est un passage de relais"""
        self.simulation.run_fast_simulation(elasped=elasped)

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

    def start_algorithm(self, aalgortim: 'AAlgorithm', *args, **kwargs) -> None:
        self.simulation.start_algorithm(aalgortim, *args, **kwargs)
    
    def stop_algorithm(self) -> None:
        self.simulation.stop_algorithm()
    
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
        
        try:
            final = queue.get_nowait()
        except Exception as e:
            self.logger.error(f"Impossible de récupérer les résultats dans la queue : {e}")
            return
        
        algostate = self.simulation.get_algorithm_manager().get_algorithm_state()
        self.algorithm_terminated.emit(algostate)

        # Vérification de la structure de final
        if not isinstance(final, list) or not all(isinstance(sublist, list) for sublist in final):
            msg = f"Structure inattendue dans la file d'attente : {final}"
            msg += f"\nExpected List[DataStorage] or List[List[DataStorage]], got {type(final)}\n\n{final}"
            self.logger.error(msg)

        qt_aircrafts_copies = self.copy_qtaircrafts()

        # Mise à jour des avions optimaux
        for aircraft_commands in final:  # Parcourt chaque liste de DataStorage pour un avion
            if not isinstance(aircraft_commands, list):
                self.logger.error(f"Expected list of DataStorage, got {type(aircraft_commands)}")
                continue

            # Récupérer l'identifiant et appliquer les commandes
            if aircraft_commands:
                id = aircraft_commands[0].id  # Les commandes sont associées à un avion par leur ID
                qtaircraft = self.qt_aircrafts.get(id)
                if qtaircraft == None:
                    self.logger.warning(f"Aucun avion trouvé pour l'ID : {id}")
                    continue

                aircraft = qtaircraft.get_aircraft()

                # Vérifier si l'avion est déjà dans la scène
                if qtaircraft not in self.scene.items():
                    #self.logger.warning(f"Avion manquant dans la scène : {aircraft.get_id_aircraft()} (recréation possible)")
                    self.scene.addItem(qtaircraft)
                
                # Mettre à jour les commandes de l'avion
                aircraft.set_commands(aircraft_commands)
                msg = f"Avion {aircraft.get_id_aircraft()} mis à jour avec {len(aircraft_commands)} commandes:\n{aircraft_commands}"
                self.logger.info(msg)

                # Assurer un Z-index élevé pour les avions originaux
                qtaircraft.setZValue(2)
        # Afficher les conflits
        """s=0
        for qtaircraft in self.qt_aircrafts.values(): 
            aircraft = qtaircraft.get_aircraft()
            for values in aircraft.get_conflicts().get_all().values():
                s += (len(values))
                print(values)
        print("len : ",s)"""
        self.enable_original_aircraft_interactions()

        # Ajouter les copies des avions (optimaux) à la scène
        for qtaircraft_copy in qt_aircrafts_copies:
            qtaircraft_copy.setOpacity(0.4)
            qtaircraft_copy.setZValue(1)  # Z-index inférieur pour apparaître sous les originaux
            self.logger.info(f"Add {qtaircraft_copy} to dictionnary")

            self.qt_aircrafts[qtaircraft_copy.get_aircraft().get_id_aircraft()] = qtaircraft_copy
            self.simulation.add_aircraft(qtaircraft_copy.get_aircraft(), register_to_manager=False)
            self.scene.addItem(qtaircraft_copy)

        self.update_qt_balises_color()

    def update_qt_balises_color(self) -> None:
        # Mettre à jour les couleurs des balises en fonction des conflits
        for qtbalise in self.qt_balises:
            balise = qtbalise.get_balise()
            conflicts = balise.get_conflicts()
            if conflicts:
                qtbalise.setBrush(QColor("red"))  # Rouge si conflits
            else:
                qtbalise.setBrush(QColor("green"))  # Vert sinon

    def cleanup(self) -> None:
        self.stop_simulation()
        self.stop_algorithm()
        self.simulation.stop_timers()

        #self.logger.info("Nettoyage des objets de l'ancienne vue...")
        self.disable_aircraft_interactions()
        
        # Supprimer les avions de la scène
        for qtaircraft in list(self.qt_aircrafts.values()):
            if self.simulation.delete_aircraft(qtaircraft.get_aircraft()):
                self.logger.info(f"Deleting aircraft id: {qtaircraft.get_aircraft().get_id_aircraft()}")
                if qtaircraft in self.scene.items():
                    self.scene.removeItem(qtaircraft)

        for qtbalise in self.qt_balises:
            if qtbalise in self.scene.items():
                self.scene.removeItem(qtbalise)

        # Nettoyer les listes internes
        self.qt_aircrafts.clear()
        self.qt_sectors.clear()
        self.qt_balises.clear()
        self.qt_routes.clear()
        
        # Déconnecter les signaux pour éviter les callbacks
        self.simulation.disconnect()
        self.disconnect()
    
    def record_simulation(self, aformatter: AFormat, awriter: AWriter) -> None:
        """"""
        """
        La méthode pour enregistrer la simulation.
        """
        filtered_positive_id = [a for a in self.simulation.get_aircrafts().values() if a.get_id_aircraft() > 0]
        formatted_data = aformatter.export(iterable=filtered_positive_id)
        return awriter.write(text=formatted_data)

    def display_arrival_manager(self, arrival_manager: ArrivalManagerWindow) -> None:
        aircraft_to_show = [a for id, a in self.simulation.get_aircrafts().items() if id > 0]
        arrival_manager.set_refresh_interval(self.timer.interval())
        arrival_manager.show_aircrafts(aircraft_to_show)
    
    def stop_threads(self) -> None:
        for thread in self.___THREADS:
            thread.join()
