from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, 
                             QWidget, QApplication,
                             QHBoxLayout, QPushButton,
                             QSlider, QLabel,
                             QGraphicsView, QGraphicsScene
)

from PyQt5.QtCore import Qt
from logging_config import setup_logging
from IHM.controller import SimulationController
from modele.utils import sec_to_time

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
        self.simulation_controller = SimulationController(self.scene)

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
        self.simulation_controller.time_updated.connect(self.update_time_label)

        # Curseur pour régler la vitesse
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 5)  # Vitesse entre 1x et 5x
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
        self.simulation_controller.reset(interval=SimulationController.INTERVAL)
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
