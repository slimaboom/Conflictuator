from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QLayout,
                             QWidget, QApplication,
                             QHBoxLayout, QPushButton,
                             QLabel, QComboBox,
                             QGraphicsView, QGraphicsScene,
                             QMenu, QAction, 
                             QInputDialog, QDialog, 
                             QDoubleSpinBox, QDialogButtonBox,
                             QProgressBar, QSlider
)

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox

from controller.controller_view import SimulationViewController
from view.QtObject import QtAircraft, ConflictWindow
from view.arrival_manager import ArrivalManagerWindow

from view.dialog.record_dialog import RecordDialog
from view.dialog.algorithm_dialog import AlgorithmParamDialog

from utils.conversion import sec_to_time, deg_aero_to_rad
from model.aircraft.speed import SpeedValue

from algorithm.interface.IAlgorithm import AlgorithmState, AAlgorithm
from algorithm.data import DataStorage

from utils.controller.dynamic_discover_packages import main_dynamic_discovering

from logging_config import setup_logging

import sys
import os
from platform import system
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from view.QtObject import QtBalise

class PlatformName(Enum):
    WINDOWS = "Windows"
    LINUX   = "Linux"
    MACOS   = "Darwin"

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.logger = setup_logging(__class__.__name__)
        
        self.setWindowTitle("Conflictuator")
        self.setGeometry(150, 80, 1500, 1100)

        self.create_simulation_view()

    def create_simulation_view(self):
        # Mise en page principale
        container = QWidget()
        self.setCentralWidget(container)

        # Création d'une scène et d'une vue pour afficher les secteurs
        self.scene = QGraphicsScene(0, 0, 1.05*self.width(), 1.05*self.height())
        self.view = QGraphicsView(self.scene, self)

        # Création des objets dans la scène
        self.simulation_controller = self.create_simulation_controller()
        self.control_panel = self.create_control_panel()

        # Fenêtre des conflits
        self.conflict_window = ConflictWindow()

        # Fenêtre des plans de vols
        self.arrival_manager = ArrivalManagerWindow()
        self.arrival_manager.closing.connect(lambda :self.arrival_manager_btn.setChecked(False))

        # Mise en page principale
        main_layout = QVBoxLayout(container)  # Mise en page verticale principale

        # Ajouter le panneau de contrôle en haut
        main_layout.addWidget(self.control_panel)

        # Ajouter une disposition horizontale pour la fenêtre des conflits et la vue principale
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.conflict_window)  # Fenêtre des conflits à gauche
        content_layout.addWidget(self.view)  # Vue principale au centre
        content_layout.addWidget(self.arrival_manager) # Fenêtre de l'arrival manager à droite (A-MAN)

        # Ajouter la disposition horizontale au layout principal
        main_layout.addLayout(content_layout)

        container.setLayout(main_layout)

        # Masquer la fenêtre des conflits au démarrage
        self.conflict_window.setVisible(False)
        # Masquer la fenêtre de l'A-MAN
        self.arrival_manager.setVisible(False)


    def create_control_panel(self):
        """Crée la barre de contrôle avec les boutons et curseurs."""
        # Découverte dynamic des algorithms, fonctions objectifs
        main_dynamic_discovering()
        
        # Créer le QWidget parent
        control_panel = QWidget()
        # Layout principal vertical pour le control panel
        vertical_layout = QVBoxLayout(control_panel)
        control_panel.setLayout(vertical_layout)

        # Première ligne : Horizontal Layout
        layout_one = QHBoxLayout()  # Disposition horizontale
        vertical_layout.addLayout(layout_one)
        
        # Deuxième ligne : Horizontal Layout
        layout_two = QHBoxLayout()  # Disposition horizontale
        vertical_layout.addLayout(layout_two)

        # Troisième ligne : Horizontal layout
        layout_tree = QHBoxLayout()
        vertical_layout.addLayout(layout_tree)

        # Première ligne : Ajout des QWidgets 
        # Bouton Play/Pause
        self.play_button = QPushButton("Play")
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.toggle_simulation)

        # Bouton Stop
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.reset_simulation)

        # Afficher le temps de simulation
        self.time_label = QLabel("Elapsed Time: 00:00:00.00")

        # Layout de vitesse (QLabel + QDoubleSpinBox)
        speed_layout = QHBoxLayout()
        # Curseur pour régler la vitesse
        self.speed_spin =  QDoubleSpinBox()
        self.speed_spin.setRange(1, 100)  # Vitesse entre 1x et 10x
        self.speed_spin.setDecimals(0)
        self.speed_spin.setValue(1)  # Par défaut, à 1
        self.speed_spin.setSingleStep(1)
        self.speed_spin.valueChanged.connect(self.update_animation_speed)

        # Afficher la vitesse
        self.speed_label = QLabel("Animation : x 1")
        self.speed_spin.valueChanged.connect(
            lambda value: self.speed_label.setText(f"Animation : x {int(value)}")
        )
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_spin)

        # Bloc de vitesse
        speed_container = QWidget()
        speed_container.setLayout(speed_layout)

        # ComboBox pour les differents algorithmes
        self.algobox_container = QWidget()
        self.combobox = QComboBox()
        
        self.algobox = QVBoxLayout(self.algobox_container)
        self.algobox.addWidget(self.combobox)

        self.algobox_container.setLayout(self.algobox)

        self.combo_options = AAlgorithm.get_available_algorithms()
        self.combobox.addItems(self.combo_options)
        
        # Connecter le signal
        self.combobox.view().pressed.connect(self.on_combobox_item_clicked)
        
        # Redéfinir showPopup
        self.combobox.showPopup = self.show_popup_combox
        
        # Ajouter les widgets à la barre
        layout_one.addWidget(self.play_button)
        layout_one.addWidget(self.stop_button)
        layout_one.addWidget(self.time_label)  # Ajouter le QLabel au panneau
        layout_one.addWidget(self.speed_label)
        layout_one.addWidget(speed_container)
        layout_one.addWidget(self.algobox_container)

        # Deuxième ligne : Ajout des QWidgets 
        # Bouton enregistrement
        self.record_sim_btn = QPushButton("Record Simulation")
        self.record_sim_btn.setCheckable(True)
        self.record_sim_btn.clicked.connect(self.record_simulation)

        # Bouton arrival manager
        self.arrival_manager_btn = QPushButton("Show A-MAN")
        self.arrival_manager_btn.setCheckable(True)
        self.arrival_manager_btn.clicked.connect(self.show_arrival_manager)

        layout_two.addWidget(self.record_sim_btn)
        layout_two.addWidget(self.arrival_manager_btn)

        # Troisième ligne : Ajout des QWidgets
        self.create_slider(layout_tree)
        return control_panel

    def create_slider(self, layout: QLayout) -> QSlider:
        self.time_slider = QSlider(Qt.Horizontal)  # Slider horizontal
        self.time_slider.setRange(0, 36000)  # 1 heure = 3600 secondes * 10 (car pas de 0.1s)
        self.time_slider.setSingleStep(1)  # Unité = 0.1s
        self.time_slider.setTickInterval(600)  # Affichage des ticks toutes les minutes (60s * 10)
        self.time_slider.setTickPosition(QSlider.TicksBelow)

        # Mettre à jour le label quand on déplace le slider
        self.time_slider.valueChanged.connect(self.update_slider)
    
        # Ajouter les widgets au layout
        layout.addWidget(self.time_slider)

    # Fonction pour mettre à jour l'affichage du temps
    def update_slider(self, value):
        seconds = value * self.simulation_controller.simulation.get_interval_timer()  # Convertir en secondes
        self.simulation_controller.run_fast_simulation(elasped=seconds)

    def show_popup_combox(self):
        """Forcer la première option sélectionnée et afficher le menu déroulant."""
        self.combobox.setCurrentIndex(0)  # Sélectionner toujours la première option
        self.combobox.view().scrollToTop()  # S'assurer que la vue commence au début
        QComboBox.showPopup(self.combobox)  # Appeler la méthode parent pour afficher le menu
    
    def freeze_interactions(self, freezing: bool) -> None:
        # Marquer le changement comme interne
        self.is_internal_change = freezing
        self.combobox.setDisabled(freezing)  # Désactiver la combobox
        self.is_internal_change = not freezing  # Réinitialiser le flag

        self.play_button.setDisabled(freezing)
        self.speed_spin.setDisabled(freezing)
        
        # Désactiver les clics sur les avions
        if freezing:
            self.simulation_controller.disable_aircraft_interactions()
        else:
            self.simulation_controller.enable_original_aircraft_interactions()
        if freezing:
            self.toggle_simulation(checked=not freezing) # False
        # Ne rien faire si freezing = False

    def on_combobox_item_clicked(self, index: QModelIndex) -> None:
        """Déclenche une action uniquement quand l'utilisateur clique sur une option."""
        selected_text = self.combobox.itemText(index.row())
        try:
            # Ne lancer un algorithm que si c'est le premier
            if not self.simulation_controller.simulation.get_algorithm_manager().has_been_lauch():
                # Gestion IHM
                self.combobox.setCurrentIndex(index.row())  # S'assurer que l'élément sélectionné reste visible
                self.freeze_interactions(True)
                self.create_algorithm_panel()

                # Gestion Algorithm class
                aalgorithm = AAlgorithm.get_algorithm_class(selected_text)
                # Demande des paramètres du constructeur de la classe dérivée AAlgorithm (dynamique)
                algorithm_dialog = AlgorithmParamDialog(algorithm_name=selected_text, parent=self)
                if algorithm_dialog.exec_() == QDialog.Accepted:
                    algo_constructor_parameters_objective_function_constructors_parameters = algorithm_dialog.get_parameters()   
                    self.simulation_controller.start_algorithm(aalgorithm, **algo_constructor_parameters_objective_function_constructors_parameters)
            else:
                self.notify_algorithm_termination(AlgorithmState.ALREADY_LAUNCH)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()

            # Construire un message d'erreur informatif
            error_msg = (
                f"Erreur dans la classe '{self.__class__.__name__}' --> {self.on_combobox_item_clicked.__qualname__}:\n\n"
                f"{tb}"
            )
            self.notify_algorithm_error(AlgorithmState.ERROR, Exception(error_msg)) # Propager l'erreur avec le traceback 

    def create_algorithm_panel(self) -> None:
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.algobox.addWidget(self.progress_bar)
        
        self.simulation_controller.simulation.signal.algorithm_progress.connect(self.update_algo_progress_bar)

        # Créer un layout horizontal pour les deux QLCDNumber
        time_layout = QHBoxLayout()

        # Temps écoulé pour l'algorithme
        elapsed_time_algo_label = QLabel("Elapsed Algorithm")
        elapsed_time_algo_label.setAlignment(Qt.AlignCenter)  # Centrer le texte horizontalement et verticalement
        style_elapsed_label = """
            QLabel {
                background-color: lightgray;
                color: black;
                border: 2px solid #8f8f91;
                border-radius: 5px;
                font-size: 15px;
                padding: 5px;
            }
        """
        elapsed_time_algo_label.setStyleSheet(style_elapsed_label)

        # QLabel pour le temps écoulé HH:MM:SS
        self.elapsed_time_display = QLabel("00:00:00")
        self.elapsed_time_display.setAlignment(Qt.AlignCenter)
        style_elapsed_display = """
            QLabel {
                background-color: lightgray;
                color: blue;
                border: 2px solid #8f8f91;
                border-radius: 5px;
                font-size: 15px;
                padding: 5px;
                font-weight: bold;
            }
        """
        self.elapsed_time_display.setStyleSheet(style_elapsed_display)

        time_layout.addWidget(elapsed_time_algo_label)
        time_layout.addWidget(self.elapsed_time_display)

        self.simulation_controller.simulation.signal.algorithm_elapsed.connect(self.update_algo_elapsed)

        # Tiemout pour l'algorithme
        timeout_algo_label = QLabel("Timeout threshold")
        timeout_algo_label.setAlignment(Qt.AlignCenter)  # Centrer le texte horizontalement et verticalement
        style_timeout_label = elapsed_time_algo_label.styleSheet() # Le meme style que elapsed_time_algo_label
        timeout_algo_label.setStyleSheet(style_timeout_label)

        # QLabel pour le timeout HH:MM:SS
        self.timeout_display = QLabel("00:00:00")
        self.timeout_display.setAlignment(Qt.AlignCenter)
        self.timeout_display.setStyleSheet("""
            QLabel {
                background-color: lightgray;
                color: red;
                border: 2px solid #8f8f91;
                border-radius: 5px;
                font-size: 15px;
                padding: 5px;
            }
        """)
        time_layout.addWidget(timeout_algo_label)
        time_layout.addWidget(self.timeout_display)

        self.simulation_controller.simulation.signal.algorithm_timeout_value.connect(self.update_algo_timeout)

        # Ajouter le layout horizontal à algobox
        self.algobox.addLayout(time_layout)

    def clear_algorithm_panel(self):
        """Supprime tous les widgets et layouts sauf le premier (la ComboBox) du panneau d'algorithme."""
        while self.algobox.count() > 1:  # Conserve le premier widget (ComboBox)
            item = self.algobox.takeAt(1)  # Commence à partir du deuxième widget
            widget_or_layout = item.widget()  # Récupère le widget (ou layout si c'est un layout)

            if widget_or_layout != None:
                # Si c'est un widget, on le supprime proprement
                widget_or_layout.deleteLater()  # Supprime le widget proprement
            else:
                # Si c'est un layout, on le supprime proprement
                layout = item.layout()
                if layout:
                    # Si le layout contient des widgets, on les supprime aussi
                    for i in range(layout.count()):
                        child_item = layout.itemAt(i)
                        child_widget = child_item.widget()
                        if child_widget != None:
                            child_widget.deleteLater()  # Supprime le widget enfant
                        else:
                            child_layout = child_item.layout()
                            if child_layout != None:
                                child_layout.deleteLater()  # Supprime le layout enfant
                    layout.deleteLater()  # Supprime le layout principal

        # Après avoir vidé le layout, on appelle update() pour réinitialiser l'affichage
        self.algobox.update()


    def update_time_label(self, time_seconds: float):
        """Met à jour le QLabel avec le temps écoulé pour la simulation hors algorithme."""
        txt = f"Elapsed Time: {sec_to_time(time_seconds)}"
        self.time_label.setText(txt)

    def create_simulation_controller(self) -> SimulationViewController:
        simulation_controller = SimulationViewController(self.scene)
        # Connexion a l'affichage du temps
        simulation_controller.chronometer.connect(self.update_time_label)
        simulation_controller.simulation.signal.simulation_finished.connect(self.simulation_finished)

        # Connexion des avions au signal clicked
        simulation_controller.connect_to_qtaircrafts(self.click_on_aircraft)

        # Connexion des balises au signal clicked
        simulation_controller.connect_to_qtbalises(self.show_conflicts_for_balise)
        
        # Connexion lors de la fin d'un algorithm pour re-enable les elements d'interactions
        simulation_controller.simulation.signal.algorithm_terminated.connect(self.connect_elements)
        simulation_controller.simulation.signal.algorithm_error.connect(self.notify_algorithm_error)
        simulation_controller.algorithm_terminated.connect(self.notify_algorithm_termination)
        return simulation_controller
    

    def click_on_aircraft(self, qtaircraft: QtAircraft) -> None:
        """Gère le clic sur un avion."""
        self.logger.info(type(qtaircraft))
        # Stopper la simulation
        self.toggle_simulation(False)

        # Création du menu
        menu = QMenu(self)

        # Titre (non sélectionnable)
        title_action = QAction(f"Identifier: {qtaircraft.get_aircraft().get_id_aircraft()}", self)
        title_action.setEnabled(False)  # Non sélectionnable
        menu.addAction(title_action)

        # Séparateur
        menu.addSeparator()

        # Action: Changer le cap
        change_heading_action = QAction("Heading change", self)
        change_heading_action.triggered.connect(lambda: self.change_aircraft_heading(qtaircraft))
        menu.addAction(change_heading_action)

        # Action: Changer la vitesse
        change_speed_action = QAction("Speed change", self)
        change_speed_action.triggered.connect(lambda: self.change_aircraft_speed(qtaircraft))
        menu.addAction(change_speed_action)

        # Afficher le menu à la position actuelle du curseur
        self.logger.info(QCursor.pos())
        menu.exec_(QCursor.pos())

    def change_aircraft_heading(self, qtaircraft: QtAircraft) -> None:
        """Permet de changer le cap d'un avion."""
        new_heading, ok = QInputDialog.getDouble(
            self,
            "Heading setting le cap",
            f"Enter new heading value for aircraft: {qtaircraft.get_aircraft().get_id_aircraft()} (in degrees) :",
            decimals=0,
            min=1,
            max=360,
            value=qtaircraft.get_aircraft().get_heading(in_aero=True)
        )
        if ok:
            nhdg = deg_aero_to_rad(new_heading)
            aircraft = qtaircraft.get_aircraft()
            time     = aircraft.get_time()
            speed    = aircraft.get_speed()
            id       = aircraft.get_id_aircraft()
            cmd      = DataStorage(id=id, time=time, speed=speed, heading=nhdg)
            qtaircraft.get_aircraft().add_command(cmd)
            # Relancer la simulation
            self.toggle_simulation(True)


    def change_aircraft_speed(self, qtaircraft: QtAircraft) -> None:
        """Permet de changer la vitesse d'un avion avec un QDoubleSpinBox."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Speed setting for aircraft: {qtaircraft.get_aircraft().get_id_aircraft()}")

        layout = QVBoxLayout()

        # Création du QDoubleSpinBox
        spin_box = QDoubleSpinBox(dialog)
        spin_box.setDecimals(5)  # Nombre de décimales
        spin_box.setRange(SpeedValue.MIN.value, SpeedValue.MAX.value)  # Plage de valeurs
        spin_box.setSingleStep(SpeedValue.STEP.value)  # Pas de 1e-4
        spin_box.setValue(qtaircraft.get_aircraft().get_speed())  # Valeur actuelle

        layout.addWidget(spin_box)

        # Ajouter les boutons "OK" et "Annuler"
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:            
            # Si l'utilisateur valide la nouvelle vitesse
            new_speed = round(spin_box.value(), 5)
            aircraft = qtaircraft.get_aircraft()
            time     = aircraft.get_time()
            id       = aircraft.get_id_aircraft()
            heading  = aircraft.get_heading()
            cmd      = DataStorage(id=id, time=time, speed=new_speed, heading=heading)
            qtaircraft.get_aircraft().add_command(cmd)
            current_balise = self.conflict_window.current_balise
            if current_balise and self.conflict_window.isVisible():
                self.conflict_window.close()
                self.show_conflicts_for_balise(current_balise)

            # Relancer la simulation
            self.toggle_simulation(True)
    
    def toggle_simulation(self, checked) -> None:
        """Lance ou met en pause la simulation."""
        self.manage_play_pause_button(checked)
        if checked:
            # Lancement des mise a jour
            self.simulation_controller.start_simulation() # Passer l'attribut a True
        else:
            self.simulation_controller.stop_simulation() # Passer l'attribut a False

    def manage_play_pause_button(self, checked: bool) -> None:
        """Bascule l'affichage du bouton entre Pause ou Play."""
        if checked:
            bg_style = "background-color: green; color: white;"
            self.play_button.setText("Pause")
            self.play_button.setStyleSheet(bg_style)
            self.logger.info(f"Simulation démarrée.")
            self.play_button.setChecked(True)
            self.time_label.setStyleSheet(bg_style)
        else:
            bg_style = "background-color: orange; color: white;"
            self.play_button.setText("Play")
            self.logger.info(f"Simulation en pause")
            self.play_button.setStyleSheet(bg_style)
            self.play_button.setChecked(False)
            self.time_label.setStyleSheet(bg_style)


    def reset_simulation(self) -> None:
        """Réinitialise la simulation."""
        bg_style = "background-color: white;"
        self.toggle_simulation(False)
        self.logger.info("Simulation réinitialisée.")
        self.play_button.setStyleSheet(bg_style)
        self.speed_spin.setValue(1) 
        # On recree un objet de SimulationViewController et on efface de la scene pour redessiner
        # Les avions sont des copies donc il faut reinitialiser tout..

        if self.simulation_controller:
            self.simulation_controller.cleanup()
            self.time_slider.setValue(0) # Déclenche les fonctions connectées

            self.scene.clear()

            self.simulation_controller = self.create_simulation_controller()
            self.simulation_controller.draw()

        self.update_time_label(0)
        self.time_label.setStyleSheet(bg_style)

        self.conflict_window.close()
        self.arrival_manager.reset()
        self.record_sim_btn.setChecked(False)
        self.arrival_manager_btn.setChecked(False)
        
        self.play_button.setDisabled(False)

        self.combobox.setDisabled(False)
        self.combobox.setCurrentIndex(0)
        self.combobox.setStyleSheet("background-color: none;")
        self.clear_algorithm_panel()

        self.speed_spin.setDisabled(False)

    def connect_elements(self):
        self.play_button.setDisabled(False)
        self.combobox.setDisabled(False)
        self.combobox.setCurrentIndex(0)
        self.speed_spin.setDisabled(False)
        self.simulation_controller.enable_original_aircraft_interactions()

    def update_animation_speed(self, value: int):
        """Met à jour la vitesse d'animation."""
        self.logger.info(f"Vitesse d'animation mise à jour : x {value}")
        if self.play_button.isChecked(): self.toggle_simulation(checked=False)
        self.simulation_controller.set_simulation_speed(speed_factor=int(value))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.simulation_controller.draw()

    def resizeEvent(self, event) -> None:
        """ Resize la fenetre principale et la scene et envoie la mise a jour au controller"""
        #self.logger.info(f"Fenetre principale redimensionnee width={self.width()}, height={self.height()}")
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def show_conflicts_for_balise(self, qtbalise: 'QtBalise') -> None:
        """Affiche les conflits associés à une balise spécifique."""
        self.conflict_window.update_conflicts(qtbalise)
        self.conflict_window.show()
    
    def notify_algorithm_error(self, algorithm_state: AlgorithmState, error: Exception) -> None:
        """Notifie une erreur lors de l'exécution de l'algorithme."""
        error_message = f"Une erreur s'est produite : {str(error)}"
        self.show_message_box(
            title="Erreur d'algorithme",
            message=f"{algorithm_state.value}\n\n{error_message}",
            is_error=True,
            algorithm_state=algorithm_state
        )
    
    def notify_algorithm_termination(self, algorithm_state: AlgorithmState) -> None:
        """Notifie l'utilisateur que l'algorithme est terminé."""
        self.combobox.setStyleSheet("background-color: none;")
        self.combobox.setEnabled(True)

        # Définir le message selon l'état
        if algorithm_state == AlgorithmState.ALREADY_LAUNCH:
            msg_text = f"{algorithm_state.value}\n\nUn algorithme a déjà été exécuté. Le lancement d'une nouvelle exécution d'algorithme est bloqué."
        else:
            msg_text = f"L'algorithme a terminé son exécution dans l'état : {algorithm_state.value}"

        self.show_message_box(
            title="Algorithme Terminé",
            message=msg_text,
            is_error=False,
            algorithm_state=algorithm_state
        )

    def show_message_box(self, title: str, message: str, is_error: bool = False, algorithm_state: AlgorithmState = None) -> None:
        """
        Affiche une boîte de dialogue pour notifier l'utilisateur.
        
        :param title: Titre de la boîte de dialogue.
        :param message: Message à afficher.
        :param is_error: Si True, utilise une icône d'erreur ; sinon, une icône d'information.
        :param algorithm_state: État de l'algorithme, utilisé pour certaines actions supplémentaires.
        """
        self.combobox.setStyleSheet("background-color: none;")
        self.combobox.setEnabled(True)

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical if is_error else QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Récupérer le bouton OK
        ok_button = msg_box.button(QMessageBox.Ok)

        # Nettoyage général au clic sur OK
        ok_button.clicked.connect(self.clear_algorithm_panel)

        # Logique supplémentaire pour réactiver l'interface si l'algorithme n'est pas terminé
        if algorithm_state and algorithm_state != AlgorithmState.FINISHED:
            def release_interaction():
                self.freeze_interactions(False)
                self.combobox.setCurrentIndex(0)
            
            ok_button.clicked.connect(release_interaction)

        # Afficher la boîte de dialogue
        msg_box.exec_()


    def update_algo_progress_bar(self, value: float) -> None:
        """
        Met à jour le style de la combobox en fonction de l'avancement de l'algorithme.
        :param value: Pourcentage d'avancement (0.0 à 100.0)
        """
        # Limiter le pourcentage entre 0 et 100
        percentage = max(0, min(100, value))
        fmt        = f"{percentage:.1f}%"
        # Changer la couleur en fonction de la progression
        if value <= 0:
            bcolor = "red"  # Vert
            color = "red"
        else:
            bcolor = "white"
            color = "blue"  # Rouge

        style = f"""
            QProgressBar {{
                border: 2px solid #8f8f91;
                border-radius: 5px;
                text-align: center;
                background-color: {bcolor};  /* Fond bcolor */
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 20px;
            }}"""

        self.progress_bar.setStyleSheet(style)
        self.progress_bar.setValue(int(percentage))
        self.progress_bar.setFormat(fmt)

        
    def update_algo_elapsed(self, elapsed: float) -> None:
        elapsed_fmt = sec_to_time(seconds=elapsed)
        self.elapsed_time_display.setText(elapsed_fmt)


    def update_algo_timeout(self, timeout: float) -> None:
        timeout_fmt = sec_to_time(seconds=timeout)
        self.timeout_display.setText(timeout_fmt)

    def record_simulation(self) -> None:
        """Enregistrer la simulation dans un thread séparé pour éviter le blocage."""
        self.record_sim_btn.setChecked(True)
        arrival_open = self.arrival_manager_btn.isChecked()
        if arrival_open:
            self.arrival_manager.setVisible(False)

        self.toggle_simulation(False)

        dialog = RecordDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Récupérer les choix de l'utilisateur
            aformatter, awritter = dialog.get_selection()
            self.logger.info(f"{aformatter}, {awritter}")

            # Afficher un message indiquant que l'enregistrement a commencé

            dialog.show_accepted_message(message='Recording...\nSimulation will start')

            # Connecter un slot temporaire pour l'enregistrement
            def recorder(is_terminated: bool):
                if is_terminated:
                    is_okay = self.simulation_controller.record_simulation(aformatter, awritter)

                    self.__on_simulation_finished(dialog, is_okay, container=awritter.get_container())
                    # Déconnecter le signal après l'exécution
                    self.simulation_controller.stop_simulation()
                    self.simulation_controller.simulation.signal.simulation_finished.disconnect(recorder)

                    self.simulation_controller.set_simulation_speed(1)
                    self.freeze_interactions(False)
                    self.toggle_simulation(False) # Démarre la simulation
                    self.play_button.setDisabled(False) # Forcer le bouton a ne pas avoir d'interaction:
                    self.arrival_manager.setVisible(False)
                    if arrival_open:
                        self.arrival_manager.setVisible(True)
                        self.arrival_manager_btn.setChecked(True)
                    else:
                        self.arrival_manager_btn.setChecked(False)

            # Connecter le signal `finished` à un slot temporaire
            self.simulation_controller.simulation.signal.simulation_finished.connect(recorder)

            # Lancer l'enregistrement
            # self.simulation_controller.set_simulation_speed(100)
            # 1h de simulation exécuté pendant l'interval du timer (0.1 sec par defaut)
            # 1h de simulation --> 0.1 temps réeel : speed_factor = TpsSim/TpsRéel
            self.simulation_controller.set_simulation_speed(36000)
            self.freeze_interactions(True)
            self.toggle_simulation(True) # Démarre la simulation
            self.play_button.setDisabled(True) # Forcer le bouton a ne pas avoir d'interaction:
            # (freeze_interactions): le bloque
            # toggle_simulation: le reactive


    def __on_simulation_finished(self, dialog: RecordDialog, is_okay: bool, container: str) -> None:
        """Cette méthode est appelée lorsque la simulation est terminée"""
        # Fermer le dialogue après que la simulation ait terminé
        if is_okay:
            msg = f'Recording Completed !\n{container}'
        else:
            msg = f'Recording Failed !\n{container}'
        dialog.show_accepted_message(message=msg)  # Afficher un message de confirmation
        dialog.accept()  # Fermer le dialogue
        self.record_sim_btn.setChecked(False)

            

    def show_arrival_manager(self) -> None:
        """Afficher l'arrival manager"""
        self.arrival_manager_btn.setChecked(True)        
        self.simulation_controller.display_arrival_manager(self.arrival_manager)

        self.arrival_manager.closing.connect(lambda :self.arrival_manager_btn.setChecked(False))

    def simulation_finished(self, is_finished: bool) -> None:
        if is_finished:
            self.toggle_simulation(not is_finished)
            
#----------------------------------------------------------------------------
#---------------------   MAIN PART  -----------------------------------------
#----------------------------------------------------------------------------

def main():

    # platforme_name: Linux | Darwin | Windows
    platform_name = system()
    if platform_name == PlatformName.LINUX.value:
        os.environ["QT_QPA_PLATFORM"] = "xcb" 
    elif platform_name == PlatformName.MACOS.value:
        os.environ["QT_QPA_PLATFORM"] = "cocoa"
    else: # Windows
        pass
    # Apres gestion de la variable d'environnement: lancement de la fenetre
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# Application PyQt5
if __name__ == "__main__":
    main()
