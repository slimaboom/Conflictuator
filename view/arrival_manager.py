
from PyQt5.QtWidgets import (QWidget, QVBoxLayout,  
                            QSpacerItem, QSizePolicy, 
                            QPushButton, QDialog, QLabel
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from collections import defaultdict


from typing import List, Dict, Tuple, TYPE_CHECKING
from typing_extensions import override

from model.conflict_manager import ConflictInformation
from utils.conversion import sec_to_time

if TYPE_CHECKING:
    from model.aircraft.aircraft import Aircraft

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
        self.buttons_deleted: Dict[int, Tuple['Aircraft', QPushButton]] = {}

        # Timer pour declencher la mise a jour des couleurs des boutons
        self.timer = None
        self.aircraft_button_format = "Aircraft %s: %s"

        # Desactivation/Activation du refresh (par exemple si la fenetre est ouverte et qu'un algorithme tourne)
        # Il y a cette erreur
        #    self.btns_layout.removeWidget(button)
        # RuntimeError: wrapped C/C++ object of type QPushButton has been deleted
        self.__is_refresh_possible = True
        self.adjustSize()
        
    def setEnabledRefresh(self, refresh_action: bool) -> bool:
        if self.isVisible():
            self.__is_refresh_possible = refresh_action

    def is_refresh_possible(self) -> bool:
        return self.__is_refresh_possible
    
    def add_aircrafts_list(self, aircraft_list: List['Aircraft']) -> None:
        for a in sorted(aircraft_list, key= lambda a: (a.get_take_off_time(), a.get_id_aircraft())):
                id = a.get_id_aircraft()
                if not id in self.buttons and not a.has_reached_final_point():
                    aircraft_btn = self.__add_aircraft_buttons(a)
                    self.buttons[id] = (a, aircraft_btn)

    def show_aircrafts(self, aircraft_list: List['Aircraft']) -> None:
        self.add_aircrafts_list(aircraft_list=aircraft_list)
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
        take_off_time = aircraft.get_take_off_time()
        conflicts = aircraft.get_conflicts()  # Dictionnaire des conflits
        
        # Construction d'un dictionnaire de balises avec les conflits associés
        conflict_balises = defaultdict(list)

        # Parcourir les conflits et organiser par balise
        for _, conflicts_list in conflicts.get_all().items():
            for conflict_info in sorted(conflicts_list, key=lambda info: info.get_conflict_time_one()):
                conflict_balises[conflict_info.get_location().get_name()].append(conflict_info)


        # Formatage du message HTML
        message = f"""
        <div>
            <b>Take Off:</b> {sec_to_time(take_off_time)}<br>

            <b>Flight Plan Estimated:</b>
            <div style="margin-left: 20px;">
                {"<br>".join([f"• <b>{wpt}</b>: {sec_to_time(time)}" for wpt, time in flight_plan_timed.items()])}
            </div><br>

            <b>Conflict Information:</b>
            <div style="margin-left: 20px; margin-top: 6px;">
                {"".join([self.__format_conflict_balise(balise, conflict_list) for balise, conflict_list in conflict_balises.items()])}
            </div><br>
        </div>
        """

        # Afficher le message dans une fenêtre dédiée
        self.__show_flight_plan(f"Plan de vol de l'avion {aircraft_id}", message)


    def __format_conflict_balise(self, balise: str, conflict_list: List['ConflictInformation']) -> str:
        """
        Formate les informations de conflit pour une balise spécifique.

        :param balise: Le nom de la balise où se produisent les conflits.
        :param conflict_list: La liste des conflits associés à cette balise.
        :return: Une chaîne HTML formatée avec les conflits.
        """
        # Construire les conflits pour cette balise
        conflicts_html = "".join([
              f"""
<div style="margin-top: 8px;">
    <div style="margin-left: 20px;">• <b>{conflict.get_aircraft_two().get_id_aircraft()}</b>: {sec_to_time(conflict.get_conflict_time_two())}</div>
    <div style="margin-left: 20px;">• <b>{conflict.get_aircraft_one().get_id_aircraft()}</b>: {sec_to_time(conflict.get_conflict_time_one())}</div>
</div>
""" for conflict in conflict_list])

        # Retourner la balise et les conflits associés avec un décalage cohérent
        return f'<div style="margin-top: 8px;">• <b>{balise}</b>:</div>{conflicts_html}'


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
            self.buttons_deleted[aircraft_id] = (aircraft, button)

        btn_text = self.aircraft_button_format % (aircraft_id, sec_to_time(aircraft.get_take_off_time()))
        button.setText(btn_text)

        # Si l'avion est déjà décollé ou sur le point de décoller
        if take_off_time <= current_time:
            button.setStyleSheet("background-color: green;")  # Vert
        # Si l'heure de décollage est dans 1 minute
        elif take_off_time <= current_time + 120:  # 60 secondes avant le décollage
            button.setStyleSheet("background-color: orange;")  # Orange
        else:
            if aircraft_id in self.buttons_deleted:
                button.setStyleSheet("background-color: gray;")  # Gris
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
            if button.isVisible():  # Vérifier si le bouton est toujours visible et existant
                self.__update_button(aircraft, button)
                self.btns_layout.removeWidget(button)  # Retirer temporairement du layout
                self.btns_layout.insertWidget(i, button)  # Réinsérer dans l'ordre trié

        if len(self.buttons_deleted) != len(self.buttons): # Si ils doivent tous etre supprimés, on les garde
            for aircraft_id, (_, button) in self.buttons_deleted.items():
                if button.isVisible():  # Vérifier si le bouton est toujours visible et existant
                    self.btns_layout.removeWidget(button)
                    button.deleteLater()
                    del self.buttons[aircraft_id]
            self.buttons_deleted.clear()

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
        try:
            for _, btn in self.buttons.values():
                btn.clicked.disconnect()  # Déconnecte tous les clics des boutons
            if self.timer:
                self.timer.timeout.disconnect()  # Déconnecte le signal timeout du timer
            super().disconnect()
        except: pass

    @override
    def setVisible(self, visible):
        if self.timer:
            if visible:
                if self.is_refresh_possible():
                    self.timer.start()
                else:
                    self.timer.stop()
            else:
                self.timer.stop()
        super().setVisible(visible)

    @override
    def hide(self) -> None:
        super().hide()
        self.closing.emit()

