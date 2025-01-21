from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, 
                             QWidget, QApplication,
                             QHBoxLayout, QPushButton,
                             QLabel, QComboBox,
                             QGraphicsView, QGraphicsScene,
                             QMenu, QAction, 
                             QInputDialog, QDialog, 
                             QDoubleSpinBox, QDialogButtonBox
)

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMessageBox

from controller.controller_view import SimulationViewController
from view.QtObject import QtAircraft, ConflictWindow
from model.utils import sec_to_time, deg_aero_to_rad
from model.aircraft import SpeedValue
from algorithm.type import AlgoType

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

        # Mise en page principale
        main_layout = QVBoxLayout(container)  # Mise en page verticale principale

        # Ajouter le panneau de contrôle en haut
        main_layout.addWidget(self.control_panel)

        # Ajouter une disposition horizontale pour la fenêtre des conflits et la vue principale
        content_layout = QHBoxLayout()
        content_layout.addWidget(self.conflict_window)  # Fenêtre des conflits à gauche
        content_layout.addWidget(self.view)  # Vue principale à droite

        # Ajouter la disposition horizontale au layout principal
        main_layout.addLayout(content_layout)

        container.setLayout(main_layout)

        # Masquer la fenêtre des conflits au démarrage
        self.conflict_window.setVisible(False)
        

    def create_control_panel(self):
        """Crée la barre de contrôle avec les boutons et curseurs."""
        control_panel = QWidget()
        layout = QHBoxLayout(control_panel)  # Disposition horizontale

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
        self.speed_spin.setRange(1, 20)  # Vitesse entre 1x et 10x
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
        self.combobox = QComboBox()
        self.combo_options = [algotype.value for algotype in AlgoType]
        self.combobox.addItems(self.combo_options)
        
        # Connecter le signal
        self.combobox.view().pressed.connect(self.on_combobox_item_clicked)
        
        # Redéfinir showPopup
        self.combobox.showPopup = self.show_popup_combox
        
        # Ajouter les widgets à la barre
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.time_label)  # Ajouter le QLabel au panneau
        layout.addWidget(self.speed_label)
        layout.addWidget(speed_container)
        layout.addWidget(self.combobox)
        
        return control_panel

    def show_popup_combox(self):
        """Forcer la première option sélectionnée et afficher le menu déroulant."""
        self.combobox.setCurrentIndex(0)  # Sélectionner toujours la première option
        self.combobox.view().scrollToTop()  # S'assurer que la vue commence au début
        QComboBox.showPopup(self.combobox)  # Appeler la méthode parent pour afficher le menu
        

    def on_combobox_item_clicked(self, index: QModelIndex) -> None:
        """Déclenche une action uniquement quand l'utilisateur clique sur une option."""
        selected_text = self.combobox.itemText(index.row())
        algo = AlgoType.find(selected_text)

        msg = f"Lauch {selected_text}"
        self.logger.info(msg)
        if algo == AlgoType.RECUIT or algo == algo.GENETIQUE:
            # Marquer le changement comme interne
            self.is_internal_change = True
            self.combobox.setCurrentIndex(index.row())  # S'assurer que l'élément sélectionné reste visible
            self.combobox.setDisabled(True)  # Désactiver la combobox
            self.is_internal_change = False  # Réinitialiser le flag

            self.play_button.setDisabled(True)
            self.speed_spin.setDisabled(True)
            
            # Désactiver les clics sur les avions
            self.simulation_controller.disable_aircraft_interactions()

            # Lancer l'algorithme
            self.toggle_simulation(checked=False)
            self.simulation_controller.simulation.start_algorithm(algo)

            # Creation de la barre de progression
            self.simulation_controller.simulation.signal.algorithm_progress.connect(self.update_progress_bar)


    def update_time_label(self, time_seconds: float):
        """Met à jour le QLabel avec le temps écoulé."""
        txt = f"Elapsed Time: {sec_to_time(time_seconds)}"
        self.time_label.setText(txt)

    def create_simulation_controller(self) -> SimulationViewController:
        simulation_controller = SimulationViewController(self.scene)
        # Connexion a l'affichage du temps
        simulation_controller.chronometer.connect(self.update_time_label)

        # Connexion des avions au signal clicked
        simulation_controller.connect_to_qtaircrafts(self.click_on_aircraft)

        # Connexion des balises au signal clicked
        simulation_controller.connect_to_qtbalises(self.show_conflicts_for_balise)
        
        # Connexion lors de la fin d'un algorithm pour re-enable les elements d'interactions
        simulation_controller.simulation.signal.algorithm_terminated.connect(self.connect_elements)
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
            qtaircraft.get_aircraft().set_heading(nhdg)
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
            qtaircraft.get_aircraft().set_speed(new_speed)            
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
            
            self.scene.clear()

            self.simulation_controller = self.create_simulation_controller()
            self.simulation_controller.draw()

        self.update_time_label(0)
        self.time_label.setStyleSheet(bg_style)

        self.conflict_window.close()
        
        self.play_button.setDisabled(False)

        self.combobox.setDisabled(False)
        self.combobox.setCurrentIndex(0)
        self.combobox.setStyleSheet("background-color: none;")

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
        self.logger.info(f"Fenetre principale redimensionnee width={self.width()}, height={self.height()}")
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def show_conflicts_for_balise(self, qtbalise: 'QtBalise') -> None:
        """Affiche les conflits associés à une balise spécifique."""
        self.conflict_window.update_conflicts(qtbalise)
        self.conflict_window.show()
    
    def notify_algorithm_termination(self):
        """Notifie l'utilisateur que l'algorithme est terminé."""
        self.combobox.setStyleSheet("background-color: none;")
        self.combobox.setEnabled(True)
        self.combobox.setEditable(False)

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Algorithme Terminé")
        msg_box.setText("L'algorithme a terminé son exécution avec succès.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def update_progress_bar(self, value: float) -> None:
        """
        Met à jour le style de la combobox en fonction de l'avancement de l'algorithme.
        :param value: Pourcentage d'avancement (0.0 à 100.0)
        """
        # Limiter le pourcentage entre 0 et 100
        percentage = max(0, min(100, value)) / 100.0
        # Si 0: processus de chauffage si algo recuit
        # Sinon: descente de temperature si algo recuit
        color = "red" if percentage <= 0 else "blue"
        stop_final = 1 if percentage <= 0 else percentage  # Si le pourcentage <= 0, stop = 1, sinon stop = percentage

        # Gradient pour le fond de la combobox
        gradient = (
            f"QComboBox {{"
            f"border: 1px solid gray;"
            f"border-radius: 3px;"
            f"padding: 5px;"
            f"background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {color}, "  # color au début
            f"stop:{stop_final:.2f} {color}, "  # color jusqu'au pourcentage
            f"stop:{stop_final:.2f} transparent, "  # Blanc au pourcentage
            f"stop:1 transparent);"  # Blanc jusqu'à la fin
            f"color: black;"  # Texte noir (même si la combobox est désactivée)            
            f"}}"
        )

        # Appliquer le style à la combobox
        self.combobox.setStyleSheet(gradient)

        # Appliquer le text
        txt = f"{value} % - {self.simulation_controller.simulation.get_algorithm().value}"
        self.combobox.setEditable(True)
        self.combobox.setCurrentText(txt)
        self.combobox.setEnabled(False)  # Assurez-vous qu'elle reste désactivée
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
