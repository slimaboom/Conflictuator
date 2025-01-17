from PyQt5.QtGui import QPen, QColor, QPolygonF, QBrush
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtWidgets import (QGraphicsItem,
                             QGraphicsPolygonItem, 
                             QGraphicsPathItem,
                             QGraphicsScene, 
                             QGraphicsTextItem,
                             QGraphicsRectItem,
                             QGraphicsEllipseItem)

from PyQt5.QtGui import QColor, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtWidgets import QPushButton

from typing import List, Dict

from model.point import Point
from model.balise import Balise
from model.aircraft import Aircraft
from model.utils import sec_to_time
from model.configuration import AIRCRAFTS
from view.signal import SignalEmitter

class QtSector(QGraphicsPolygonItem):
    def __init__(self, sector_name: str, parent: QGraphicsScene):
        super().__init__()
        self.sector_name = sector_name
        self.parent = parent
    
    def add_polygon(self, points: List[Point], qcolor: QColor) -> None:
        # Definir le polygone pour chaque secteur
        w, h = self.parent.width(), self.parent.height()

        polygon = QPolygonF([QPointF(point.getX()*w, (1-point.getY())*h) for point in points])
        self.setBrush(qcolor)
        #self.setPen(QPen(Qt.black, 1))
        self.setPolygon(polygon)

class QtBalise(QGraphicsPolygonItem):
    def __init__(self, balise: Balise, parent: QGraphicsScene):
        super().__init__()
        self.balise = balise
        self.parent = parent
    
        # Taille du triangle
        self.size_triangle = 10

        # Ajout d'un signal pour les clics
        self.signal = SignalEmitter()
    
    def get_balise(self) -> Balise: return self.balise
    
    def makePolygon(self, qcolor: QColor) -> None:
        x, y = self.balise.getXY()
        y = 1 - y
        width, height = self.parent.width(), self.parent.height()
        polygon = QPolygonF([QPointF(x * width, y * height - self.size_triangle), 
                  QPointF(x * width - self.size_triangle, y * height + self.size_triangle), 
                  QPointF(x * width + self.size_triangle, y * height + self.size_triangle)]
                  )
        self.setBrush(qcolor)
        self.setPolygon(polygon)

        # Ajouter le texte pour le nom de la balise 
        self.text_item = QGraphicsTextItem(self.balise.get_name(), self) 
        self.text_item.setPos(x * width, y *  height + self.size_triangle) 
        self.text_item.setDefaultTextColor(Qt.black)

    def mousePressEvent(self, event):
        """Gère l'événement de clic et émet un signal."""
        self.signal.clicked.emit(self.balise)  # Transmet la balise cliquée
        super().mousePressEvent(event)

class QtAirway(QGraphicsPathItem):
    def __init__(self, airway_name: str, parent: QGraphicsScene):
        super().__init__()
        self.name = airway_name
        self.parent = parent
    
    def add_path(self, balises: List[Balise], qcolor: QColor) -> None:
        path = QPainterPath()
        width, height = self.parent.width(), self.parent.height()
        points = [QPointF(balise.getX() * width, (1-balise.getY()) * height) for balise in balises]
        if points:
            path.moveTo(points[0])
            for point in points[1:]: path.lineTo(point)
        
        self.setPath(path)
        self.setPen(QPen(qcolor, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

class QtAircraft(QGraphicsPolygonItem):
    def __init__(self, aircraft: Aircraft, parent: QGraphicsScene, qcolor: Qt.GlobalColor):
        super().__init__()
        self.aircraft = aircraft
        self.parent = parent
        self.history_drawing = {}
        self.qcolor = qcolor

        # Dessiner l'avion (carré noir)
        self.draw_aircraft()

        # Ajouter une etiquette a l'avion
        self.setAcceptHoverEvents(True)
        self.initialise_tooltip()

        # Emetteur de signaux
        self.signal = SignalEmitter()
        
        # Cela permet à l'élément d'écouter les événements de la souris
        self.setFlag(QGraphicsItem.ItemIsSelectable)  

    def get_aircraft(self) -> Aircraft: return self.aircraft
    def set_aircraft_id(self, id: int) -> None:
        self.aircraft.set_aircraft_id(id)
        
    def initialise_tooltip(self) -> QGraphicsTextItem:
        qgraphictextitem = QGraphicsTextItem("", self)
        qgraphictextitem.setDefaultTextColor(Qt.black)
        qgraphictextitem.setVisible(False)

        self.tooltip = qgraphictextitem

        # Créer un objet pour le fond (rectangle)
        tooltip_background = QGraphicsRectItem(self)
        tooltip_background.setBrush(QBrush(QColor(220, 220, 220, 25)))  # Gris clair avec opacité alpha
        tooltip_background.setPen(QPen(Qt.NoPen))  # Pas de bordure
        tooltip_background.setVisible(False)

        self.tooltip_background = tooltip_background


    def _get_square(self, x: float, y: float, size: float) -> QPolygonF:
        half_size = size / 2
        square = QPolygonF([
            QPointF(x - half_size, y - half_size),
            QPointF(x + half_size, y - half_size),
            QPointF(x + half_size, y + half_size),
            QPointF(x - half_size, y + half_size)]
        )
        return square

    def draw_aircraft(self) -> None:
        size_square = 12 # Taille d'un coté du carré

        x = self.aircraft.get_position().getX() * self.parent.width()
        y = (1 - self.aircraft.get_position().getY()) * self.parent.height()

        square = self._get_square(x, y, size=size_square)
        self.setPolygon(square)

        # Definir les propietes visuelles du triangle
        self.setBrush(QColor(self.qcolor))
        self.setOpacity(self.opacity())
        self.setPen(QPen(self.qcolor, 1))

    def draw_history(self, speed_factor) -> None:
        max_history_points = 6
        step_points = 50
        history_keys = sorted(self.aircraft.get_history().keys(), reverse=True)[::step_points][:max_history_points]
        scale_factor = 1.0

        # Supprimer les anciens items d'history
        for _, item in self.history_drawing.items():
            self.parent.removeItem(item)
        self.history_drawing.clear()

        # Redessiner l'historique
        for i, time_key in enumerate(history_keys):
            info = self.aircraft.get_history()[time_key]
            hist_pos = info.get_position()

            x = hist_pos.getX() * self.parent.width()
            y = (1 -  hist_pos.getY()) * self.parent.height()

            # Definir la taille du carre qui diminue avec l'age dans l'historique
            size_square = int(8 * (scale_factor - ((i+1)/max_history_points)))

            #square = self._get_square(x, y, size=size_square)
            bounding_rect = QRectF(x - size_square, y - size_square, 2 * size_square, 2 * size_square)

            item = QGraphicsEllipseItem(bounding_rect)
            brush = QBrush(QColor(self.qcolor))
            item.setPen(QPen(self.qcolor, 1))
            item.setBrush(brush)
            item.setOpacity(1 - (i+1)/max_history_points)

            # Definir les propietes visuelles du triangle
            # Ajouter la representation dans history_drawing
            self.history_drawing[time_key] = item
            
            # Ajouter la representation dans la scene
            self.parent.addItem(item)

    def update(self, timestep: float, speed_factor: int) -> None:
        for _ in range(speed_factor):
            self.aircraft.update(timestep) # Mouvement en backend
        self.draw_history(speed_factor)  # Redessine l'historique
        self.draw_aircraft() # Redessine l'avion

    # Gestion des événements de survol
    def hoverEnterEvent(self, event):
        # Appeler la méthode parente
        super().hoverEnterEvent(event)

        # Récupérer les données de l'avion
        identifiant = self.aircraft.get_id_aircraft()
        speed = self.aircraft.get_speed()
        heading = round(self.aircraft.get_heading(in_aero=True), 2)
        x, y, z = self.aircraft.get_position().getXYZ()
        time = sec_to_time(self.aircraft.get_time())
        takeoff = sec_to_time(self.aircraft.get_take_off_time())
        # Mettre à jour le texte de l'info-bulle
        tooltip_text = f"""
<div style="font-size: 10pt; color: black;">
    Idt: <span style="color: blue;"><b>{identifiant}</b></span>
    Alt: <span style="color: blue;"><b>{z}</b></span>
    V: <span style="color: blue;"><b>{speed}</b> unité/s</span>
    Hdg: <span style="color: blue;"><b>{heading} ° </b></span>
    Time: <span style="color: blue;"><b>{time}</b></span>
    Take Off: <span style="color: blue";"><b>{takeoff}</b></span>
</div>"""
        
        self.tooltip.setHtml(tooltip_text)

        # Positionner et afficher l'info-bulle
        x = x * self.parent.width()
        y = (1 - y) * self.parent.height()

        # Ajuster la taille et la position du fond (rectangle)
        bounding_rect = self.tooltip.boundingRect()
        self.tooltip_background.setRect(bounding_rect)  # Ajout d'une marge autour du texte
        self.tooltip_background.setPos(x, y)
        self.tooltip_background.setOpacity(0.5)
        
        # Afficher l'info-bulle
        self.tooltip_background.setVisible(True)
        self.tooltip.setVisible(True)
        self.tooltip.setPos(x, y)

    def hoverLeaveEvent(self, event):
        # Appeler la méthode parente
        super().hoverLeaveEvent(event)

        # Cacher l'info-bulle
        self.tooltip.setVisible(False)
        self.tooltip_background.setVisible(False)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Lorsque l'utilisateur presse la souris, "attraper" la souris
        self.signal.clicked.emit(self)

    def mouseReleaseEvent(self, event):
        # Lorsque l'utilisateur relâche la souris, "délivrer" la souris
        super().mouseReleaseEvent(event)  # Appeler la méthode parente
        self.signal.clicked.emit(self)  # Émettre le signal clicked
        super().mouseReleaseEvent(event)  # Appeler la méthode parente

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.aircraft.get_id_aircraft()}, speed={self.aircraft.get_speed()}, hdg={self.aircraft.get_heading(in_aero=True)})"

class ConflictWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conflits détectés")

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

        self._current_balise: QtBalise = None

    @property
    def current_balise(self) -> QtBalise: return self._current_balise

    def update_conflicts(self, qtbalise: QtBalise) -> None:
        """Met à jour l'affichage avec la liste des conflits."""
        self._current_balise = qtbalise
        balise = qtbalise.get_balise()
        conflicts = balise.get_conflicts()
        if not conflicts:
            self.conflict_display.setText("<b>Aucun conflit détecté.</b>")
        else:
            text = f"<h3>Balise : {balise.get_name()}</h3><ul>"
            for conflict in conflicts:

                text = self.add_conflict_text(conflict, text)

            self.conflict_display.setHtml(text)
    
    def add_conflict_text(self, conflict: Dict[str, float], text1: str) -> str:
        aircraft_id1 = conflict["aircraft_1"]
        aircraft_1 = AIRCRAFTS.get_from_key(aircraft_id1)
        aircraft_id2 = conflict["aircraft_2"]
        aircraft_2 = AIRCRAFTS.get_from_key(aircraft_id2)
        conflict_time = conflict["time_1"]
        time2 = conflict['time_2']

        text = text1
        v1 = f"{aircraft_1.get_speed():.1e}".replace('.0', '')
        v2 = f"{aircraft_2.get_speed():.1e}".replace('.0', '')
        # Ajout du style CSS pour décaler légèrement le texte vers la gauche
        text += """
        <style>
            .conflict {
                margin-left: -10px;  /* Décale légèrement le contenu à gauche */
            }
        </style>
        <div class="conflict">
        """
        text += f"""
            <b> Time : </b> {sec_to_time(conflict_time)}<br>({conflict_time} s)<br>
            <li>
                <b>Avion 1 :</b> {aircraft_id1}<br>
                <b>Arrive à:</b> {sec_to_time(conflict_time)}<br>
                <b>Position :</b> ({aircraft_1.get_position().getX():.2f}, 
                                    {aircraft_1.get_position().getY():.2f})<br>
                <b>Vitesse :</b> {v1} unité/s<br>
                <b>Cap :</b> {aircraft_1.get_heading(in_aero=True):.2f}°<br>
                <br>
                <b>Avion 2 :</b> {aircraft_id2}<br>
                <b>Arrive à:</b> {sec_to_time(time2)} <br>
                <b>Position :</b> ({aircraft_2.get_position().getX():.2f}, 
                                    {aircraft_2.get_position().getY():.2f})<br>
                <b>Vitesse :</b> {v2} unité/s/s<br>
                <b>Cap :</b> {aircraft_2.get_heading(in_aero=True):.2f}°<br>
                <br>
                </li>
        """
        text += "</div></ul>"
        return text