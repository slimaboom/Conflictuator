
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtWidgets import QPushButton


class ArrivalManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A-MAN")

        # Configuration de la mise en page
        layout = QVBoxLayout(self)

        self.title_label = QLabel("Conflits détectés :")
        self.conflict_display = QTextEdit()
        self.conflict_display.setReadOnly(True)  # Zone non modifiable

        # Bouton de fermeture
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.hide)  # Connecte le clic pour cacher la fenêtre

        # Ajouter les widgets à la mise en page
        layout.addWidget(self.title_label)
        layout.addWidget(self.conflict_display)
        layout.addWidget(self.close_button)

