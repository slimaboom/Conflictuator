from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, 
                             QWidget, QApplication,
                             QHBoxLayout, QPushButton,
                             QSlider, QLabel,
                             QGraphicsView, QGraphicsScene,
                             QMenu, QAction, 
                             QInputDialog, QDialog, 
                             QDoubleSpinBox, QDialogButtonBox
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from logging_config import setup_logging
from IHM.controller import SimulationController
from IHM.QtObject import QtAircraft, ConflictWindow
from modele.utils import sec_to_time, deg_aero_to_rad

import sys
import os
from platform import system
from enum import Enum

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
        self.time_label = QLabel("Temps: 00:00:00.00")

        # Layout de vitesse (QLabel + QDoubleSpinBox)
        speed_layout = QHBoxLayout()
        # Curseur pour régler la vitesse
        self.speed_spin =  QDoubleSpinBox()
        self.speed_spin.setRange(1, 20)  # Vitesse entre 1x et 10x
        self.speed_spin.setDecimals(0)
        self.speed_spin.setValue(1)  # Par défaut, à 1
        self.speed_spin.setSingleStep(1)
        self.speed_spin.valueChanged.connect(self.update_speed)

        # Afficher la vitesse
        self.speed_label = QLabel("Vitesse : x1")
        self.speed_spin.valueChanged.connect(
            lambda value: self.speed_label.setText(f"Vitesse : x {int(value)}")
        )
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_spin)

        # Bloc de vitesse
        speed_container = QWidget()
        speed_container.setLayout(speed_layout)

        # Ajouter les widgets à la barre
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.time_label)  # Ajouter le QLabel au panneau
        layout.addWidget(self.speed_label)
        layout.addWidget(speed_container)
        
        return control_panel

    def update_time_label(self, time_seconds: float):
        """Met à jour le QLabel avec le temps écoulé."""
        self.time_label.setText(f"Temps: {sec_to_time(time_seconds)}")

    def create_simulation_controller(self) -> SimulationController:
        simulation_controller = SimulationController(self.scene)
        
        # Connexion des avions au signal clicked
        for _, qtaircraft in simulation_controller.get_aircrafts().get_all().items():
            # Connexion des avions sur le signal clicked
            qtaircraft.signal_emitter.clicked.connect(self.click_on_aircraft)
        
        # Connexion a l'affichage du temps
        simulation_controller.time_updated.connect(self.update_time_label)

        # Connexion des balises au signal clicked
        for _, qtbalise in simulation_controller.get_balises().get_all().items():
            qtbalise.signal_emitter.clicked.connect(
                lambda _, balise=qtbalise.get_balise(): self.show_conflicts_for_balise(balise)
            )
        return simulation_controller
    

    def reset_connexion(self):
        # Connexion des avions au signal clicked
        for _, qtaircraft in self.simulation_controller.get_aircrafts().get_all().items():
            qtaircraft.signal_emitter.clicked.connect(lambda: self.toggle_simulation(False))
        # Connexion des balises au signal clicked
        for _, qtbalise in self.simulation_controller.get_balises().get_all().items():
            qtbalise.signal_emitter.clicked.connect(
                lambda _, balise=qtbalise.get_balise(): self.show_conflicts_for_balise(balise)
            )
        return None


    def click_on_aircraft(self, qtaircraft: QtAircraft) -> None:
        """Gère le clic sur un avion."""
        # Stopper la simulation
        self.toggle_simulation(False)
        # Création du menu
        menu = QMenu(self)

        # Titre (non sélectionnable)
        title_action = QAction(f"Identifiant: {qtaircraft.get_aircraft().get_id_aircraft()}", self)
        title_action.setEnabled(False)  # Non sélectionnable
        menu.addAction(title_action)

        # Séparateur
        menu.addSeparator()

        # Action: Changer le cap
        change_heading_action = QAction("Changer le cap", self)
        change_heading_action.triggered.connect(lambda: self.change_aircraft_heading(qtaircraft))
        menu.addAction(change_heading_action)

        # Action: Changer la vitesse
        change_speed_action = QAction("Changer la vitesse", self)
        change_speed_action.triggered.connect(lambda: self.change_aircraft_speed(qtaircraft))
        menu.addAction(change_speed_action)

        # Afficher le menu à la position actuelle du curseur
        menu.exec_(QCursor.pos())

    def change_aircraft_heading(self, qtaircraft: QtAircraft) -> None:
        """Permet de changer le cap d'un avion."""
        new_heading, ok = QInputDialog.getDouble(
            self,
            "Changer le cap",
            f"Entrez le nouveau cap pour l'avion {qtaircraft.get_aircraft().get_id_aircraft()} (en degrés) :",
            decimals=0,
            min=1,
            max=360,
            value=qtaircraft.get_aircraft().get_heading(in_aero=True)
        )
        if ok:
            nhdg = deg_aero_to_rad(new_heading)
            qtaircraft.get_aircraft().set_heading(nhdg)
            print(f"Cap de l'avion {qtaircraft.get_aircraft().get_id_aircraft()} mis à jour : {nhdg} ({new_heading}°)")
            # Relancer la simulation
            self.toggle_simulation(True)


    def change_aircraft_speed(self, qtaircraft: QtAircraft) -> None:
        """Permet de changer la vitesse d'un avion avec un QDoubleSpinBox."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Changer la vitesse pour l'avion {qtaircraft.get_aircraft().get_id_aircraft()}")

        layout = QVBoxLayout()

        # Création du QDoubleSpinBox
        spin_box = QDoubleSpinBox(dialog)
        spin_box.setDecimals(5)  # Nombre de décimales
        spin_box.setRange(1e-5, 9e-4)  # Plage de valeurs
        spin_box.setSingleStep(1e-5)  # Pas de 1e-5
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
            print(f"Vitesse de l'avion {qtaircraft.get_aircraft().get_id_aircraft()} mise à jour : {new_speed}")
            # Relancer la simulation
            self.toggle_simulation(True)
    
    def toggle_simulation(self, checked):
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


    def reset_simulation(self):
        """Réinitialise la simulation."""
        bg_style = "background-color: white;"
        self.toggle_simulation(False)
        self.logger.info("Simulation réinitialisée.")
        self.play_button.setStyleSheet(bg_style)
        self.speed_spin.setValue(1)
        # On recree un objet de SimulationController et on efface de la scene pour redessiner
        # Les avions sont des copies donc il faut reinitialiser tout..
        self.scene.clear()
        self.simulation_controller = self.create_simulation_controller()
        self.simulation_controller.draw()

        self.update_time_label(0)
        self.time_label.setStyleSheet(bg_style)


    def update_speed(self, value):
        """Met à jour la vitesse d'animation."""
        self.logger.info(f"Vitesse d'animation mise à jour : x {value}")
        if self.play_button.isChecked(): self.toggle_simulation(checked=False)
        self.simulation_controller.set_speed(speed_factor=value)

    def showEvent(self, event):
        super().showEvent(event)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.simulation_controller.draw()

    def resizeEvent(self, event):
        """ Resize la fenetre principale et la scene et envoie la mise a jour au controller"""
        self.logger.info(f"Fenetre principale redimensionnee width={self.width()}, height={self.height()}")
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def show_conflicts_for_balise(self, balise):
        """Affiche les conflits associés à une balise spécifique."""
        self.conflict_window.update_conflicts(balise)
        self.conflict_window.show()

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
