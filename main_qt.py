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
from IHM.QtObject import QtAircraft
from modele.utils import sec_to_time, deg_aero_to_rad

import sys
import os


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
        self.scene = QGraphicsScene(0, 0, self.width(), self.height())
        self.view = QGraphicsView(self.scene, self)

        # Création des objets dans la scene
        self.simulation_controller = self.create_simulation_controller()

        self.control_panel = self.create_control_panel()

        layout = QVBoxLayout(container)
        layout.addWidget(self.control_panel)  # Barre de contrôle en haut
        container.setLayout(layout)
        layout.addWidget(self.view)


    def create_control_panel(self):
        """Crée la barre de contrôle avec les boutons et curseurs."""
        control_panel = QWidget()
        layout = QHBoxLayout(control_panel)

        # Bouton Play/Pause
        self.play_button = QPushButton("Play")
        self.play_button.setCheckable(True)
        self.play_button.clicked.connect(self.toggle_simulation)

        # Bouton Stop
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.reset_simulation)

        # Afficher le temps de simulation
        self.time_label = QLabel("Temps: 00:00:00.00")

        # Curseur pour régler la vitesse
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)  # Vitesse entre 1x et 10x
        self.speed_slider.setValue(1)  # Par défaut, à 1
        self.speed_slider.valueChanged.connect(self.update_speed)

        # Afficher la vitesse
        self.speed_label = QLabel("Vitesse : x1")
        self.speed_slider.valueChanged.connect(
            lambda value: self.speed_label.setText(f"Vitesse : x {value}")
        )

        # Ajouter les widgets à la barre
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.time_label)  # Ajouter le QLabel au panneau
        layout.addWidget(QLabel("Vitesse"))
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_label)
        
        return control_panel

    def update_time_label(self, time_seconds: float):
        """Met à jour le QLabel avec le temps écoulé."""
        self.time_label.setText(f"Temps: {sec_to_time(time_seconds)}")

    def create_simulation_controller(self) -> SimulationController:
        # Creation du SimulationController
        simulation_controller = SimulationController(self.scene)
        for _, qtaircraft in simulation_controller.get_aircrafts().get_all().items():
            # Connexion des avions sur le signal clicked
            qtaircraft.signal_emitter.clicked.connect(self.click_on_aircraft)
        
        # Connexion a l'affichage du temps
        simulation_controller.time_updated.connect(self.update_time_label)
        return simulation_controller


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
        self.speed_slider.setValue(1)
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




# Application PyQt5
if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"] = "xcb"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
