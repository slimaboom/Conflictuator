
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,  
                            QSpacerItem, QSizePolicy, 
                            QPushButton, QDialog, QLabel
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from typing import List, Dict, Tuple, TYPE_CHECKING
from typing_extensions import override

from model.conflict_manager import ConflictInformation
from utils.conversion import sec_to_time

if TYPE_CHECKING:
    from model.aircraft import Aircraft

class ArrivalManagerWindow(QWidget):
    # Signal émettant l'ID de l'avion sélectionné
    closing = pyqtSignal()

    def __init__(self,  parent=None):
        """
        Initialise le gestionnaire des arrivées des avions.
        :param parent: Le parent QWidget.
        """
        super().__init__(parent)
        self.setWindowTitle("Arrival Manager")
        self.setGeometry(100, 100, 600, 500)  # Position et taille initiale

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Layout pour les boutons (2ème ligne)
        self.btns_layout = QVBoxLayout()
        self.btns_layout.setSpacing(5)  # Espacement entre les boutons
        self.main_layout.addLayout(self.btns_layout)

        # Spacer pour occuper l'espace vide (avant le bouton Close)
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(self.spacer)

        # Bouton de fermeture
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.hide)  # Connecte le clic pour cacher la fenêtre
        self.main_layout.addWidget(self.close_button)

        # Stockage des boutons
        self.buttons: Dict[int, Tuple['Aircraft', QPushButton]] = {}
        # Timer pour declencher la mise a jour des couleurs des boutons
        self.timer = None
        self.aircraft_button_format = "Aircraft %s: %s"
    
    def show_aircrafts(self, aircraft_list: List['Aircraft']):
        for a in sorted(aircraft_list, key= lambda a: (a.get_take_off_time(), a.get_id_aircraft())):
            id = a.get_id_aircraft()
            if not id in self.buttons:
                aircraft_btn = self.__add_aircraft_buttons(a)
                self.buttons[id] = (a, aircraft_btn)

        self.setVisible(True)

    def __add_aircraft_buttons(self, aircraft: 'Aircraft') -> QPushButton:
        """
        Ajoute un bouton pour un avion spécifique.

        :param aircraft: L'avion.
        """
        aircraft_id = aircraft.get_id_aircraft()
        btn_text = self.aircraft_button_format % (aircraft_id, sec_to_time(aircraft.get_take_off_time()))
        button = QPushButton(btn_text)
        button.clicked.connect(lambda: self.__on_aircraft_clicked(aircraft_id))
        self.btns_layout.addWidget(button)
        return button


    def __on_aircraft_clicked(self, aircraft_id: str):
        """
        Gère le clic sur un bouton d'avion.
        Affiche le plan de vol de l'avion sélectionné.

        :param aircraft_id: L'identifiant de l'avion sélectionné.
        """
        # Récupérer l'objet Aircraft associé à l'ID
        aircraft = self.buttons[aircraft_id][0]  # Stocker l'avion dans `self.buttons`

        # Construire le message HTML des informations de l'avion
        flight_plan_timed = aircraft.get_flight_plan_timed()  # Retourne un dictionnaire ou une liste de tuples (balise, temps)
        take_off_time     = aircraft.get_take_off_time()
        conflicts         = aircraft.get_conflicts()

        message = f"""
        <div>
            <b>Take Off:</b> {sec_to_time(take_off_time)}<br><br>

            <b>Flight Plan Estimated:</b><br>
            <div style="margin-left: 20px;">
                {"<br>".join([f"• <b>{wpt}</b>: {sec_to_time(time)}" for wpt, time in flight_plan_timed.items()])}
            </div><br>

            <b>Conflict Information:</b><br>
            <div style="margin-left: 20px;">
                {"<br>".join([self.__format_conflict_info(conflict_info) for conflict_info in conflicts.get_all().values()])}            
            </div>
        </div>
        """

        # Afficher le message dans une fenêtre dédiée
        self.__show_flight_plan(title=f"Flight Plan of aircraft: {aircraft_id}", message=message)


    def __format_conflict_info(self, conflict: ConflictInformation) -> str:
        """
        Formate les informations d'un conflit pour l'affichage.
        
        :param conflict: L'objet ConflictInformation.
        :return: La chaîne formatée pour un conflit spécifique.
        """
        aircraft_one_id = conflict.get_aircraft_one().get_id_aircraft()
        aircraft_two_id = conflict.get_aircraft_two().get_id_aircraft()
        conflict_time_one = sec_to_time(conflict.get_conflict_time_one())
        conflict_time_two = sec_to_time(conflict.get_conflict_time_two())
        location = conflict.get_location().get_name()

        html = f"""• <b>Conflict between Aircraft {aircraft_one_id} and Aircraft {aircraft_two_id}</b><br>
        Location: <b>{location}</b><br>
        Times: Aircraft {aircraft_one_id}: {conflict_time_one} | Aircraft {aircraft_two_id}: {conflict_time_two}
"""
        return html

    def __show_flight_plan(self, title: str, message: str) -> None:
        """
        Affiche une fenêtre dédiée avec le plan de vol formaté en HTML.

        :param title: Le titre de la fenêtre.
        :param message: Le contenu formaté du plan de vol en HTML.
        """
        # Créer une nouvelle fenêtre (QDialog)
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(400, 300)

        # Ajouter un QLabel pour afficher le texte HTML
        label = QLabel(dialog)
        label.setText(f"<div style='font-size: 14px; line-height: 1.6;'>{message}</div>")  # Appliquer du style HTML
        label.setWordWrap(True)  # Permet au texte de s'enrouler
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Alignement à gauche en haut

        # Ajouter un layout pour gérer la disposition
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)

        # Bouton de fermeture
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        # Afficher la fenêtre
        dialog.exec_()


    def __update_button(self, aircraft: 'Aircraft', button: QPushButton) -> None:
        """Mise à jour de le bouton de l'avion en fonction du décollage de l'avion."""
        
        # Récupérer l'heure actuelle et l'heure de décollage
        current_time = aircraft.get_time()
        take_off_time = aircraft.get_take_off_time()
        aircraft_id = aircraft.get_id_aircraft()

        if aircraft.has_reached_final_point():
            # Déconnecter les signaux et les slots du bouton avant de le supprimer
            self.btns_layout.removeWidget(button)
            button.deleteLater()
            del self.buttons[aircraft_id]

        btn_text = self.aircraft_button_format % (aircraft_id, sec_to_time(aircraft.get_take_off_time()))
        button.setText(btn_text)

        # Si l'avion est déjà décollé ou sur le point de décoller
        if take_off_time <= current_time:
            button.setStyleSheet("background-color: green;")  # Vert
        # Si l'heure de décollage est dans 1 minute
        elif take_off_time <= current_time + 120:  # 60 secondes avant le décollage
            button.setStyleSheet("background-color: orange;")  # Orange
        else:
            button.setStyleSheet("")  # Pas de couleur, ou reset à l'état initial


    def set_refresh_interval(self, interval: int) -> None:
        if self.timer == None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.__refresh_button)
            self.timer.setInterval(interval)

    def __refresh_button(self) -> None:
        """Met à jour les boutons en fonction de l'avancement des avions."""

        # Trier les boutons en fonction de l'heure de décollage de l'avion
        sorted_buttons = sorted(self.buttons.items(), key=lambda x: x[1][0].get_take_off_time())

        # Réorganiser les boutons dans le layout sans les supprimer ni les réajouter
        for i, (aircraft_id, (aircraft, button)) in enumerate(sorted_buttons):
            self.__update_button(aircraft, button)
            self.btns_layout.removeWidget(button)  # Retirer temporairement du layout
            self.btns_layout.insertWidget(i, button)  # Réinsérer dans l'ordre trié


    def __remove_btns(self) -> None:
        """Supprime les boutons de l'interface et de leur layout."""
        for _, btn in self.buttons.values():
            self.btns_layout.removeWidget(btn)  # Supprime le bouton du layout
            btn.deleteLater()  # Supprime le widget
        self.buttons.clear()  # Vide le dictionnaire des boutons

    def reset(self) -> None:
        """
        Réinitialise la fenêtre : supprime les boutons, stoppe le timer et désactive les connexions.
        """
        self.hide()  # Cache la fenêtre
        self.disconnect()  # Déconnecte tous les signaux et slots
        self.__remove_btns()  # Supprime les boutons de l'interface
        if self.timer:  # Si un timer existe, on l'arrête et on le supprime
            self.timer.stop()
            self.timer.deleteLater()
            self.timer = None

    @override
    def disconnect(self) -> None:
        """
        Déconnecte tous les signaux associés aux boutons.
        """
        for _, btn in self.buttons.values():
            btn.clicked.disconnect()  # Déconnecte tous les clics des boutons
        if self.timer:
            self.timer.timeout.disconnect()  # Déconnecte le signal timeout du timer
        super().disconnect()


    @override
    def setVisible(self, visible):
        if self.timer:
            if visible:
                self.timer.start()
            else:
                self.timer.stop()
        super().setVisible(visible)

    @override
    def hide(self) -> None:
        super().hide()
        self.closing.emit()

