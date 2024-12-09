from PyQt5.QtGui import QPen, QColor, QPolygonF, QBrush
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import (QGraphicsPolygonItem, 
                             QGraphicsPathItem,
                             QGraphicsScene, 
                             QGraphicsTextItem,
                             QGraphicsRectItem)

from PyQt5.QtGui import QColor, QPainterPath

from typing import List

from modele.point import Point
from modele.balise import Balise
from modele.aircraft import Aircraft

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
    
    def makePolygon(self, qcolor: QColor) -> None:
        x, y = self.balise.getXY()
        y = 1 - y
        width, height = self.parent.width(), self.parent.height()
        polygon = QPolygonF([QPointF(x * width, y * height - self.size_triangle), 
                  QPointF(x * width - self.size_triangle, y * height + self.size_triangle), 
                  QPointF(x * width + self.size_triangle, y * height + self.size_triangle)]
                  )
        self.setBrush(qcolor)
        #self.setPen(QPen(Qt.black, 1))
        self.setPolygon(polygon)

        # Ajouter le texte pour le nom de la balise 
        self.text_item = QGraphicsTextItem(self.balise.get_name(), self) 
        self.text_item.setPos(x * width, y *  height + self.size_triangle) 
        self.text_item.setDefaultTextColor(Qt.black)

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
    def __init__(self, aircraft: Aircraft, parent: QGraphicsScene):
        super().__init__()
        self.aircraft = aircraft
        self.parent = parent
        self.history_drawing = {}

        # Dessiner l'avion (carré noir)
        self.draw_aircraft()

        # Ajouter une etiquette a l'avion
        self.setAcceptHoverEvents(True)
        self.initialise_tooltip()
    
    def get_aircraft(self) -> Aircraft: return self.aircraft

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

        half_size = size_square/2
        square = self._get_square(x, y, size=size_square)
        self.setPolygon(square)

        # Definir les propietes visuelles du triangle
        self.setBrush(QColor(Qt.black))
        self.setPen(QPen(Qt.black, 1))
    
    def draw_history(self, speed_factor) -> None:
        max_history_points = 20
        step_points = 15*speed_factor
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

            square = self._get_square(x, y, size=size_square)
            item = QGraphicsPolygonItem(square)

            # Definir les propietes visuelles du triangle
            brush = QBrush(QColor(Qt.black))
            item.setBrush(brush)
            item.setPen(QPen(Qt.black, 1))

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
        time = round(self.aircraft.get_time(), 5)
        # Mettre à jour le texte de l'info-bulle
        tooltip_text = f"""
<div style="font-size: 10pt; color: black;">
    Idt: <span style="color: blue;"><b>{identifiant}</b></span>
    Alt: <span style="color: blue;"><b>{z}</b></span>
    V: <span style="color: blue;"><b>{speed}</b> unit</span>
    Hdg: <span style="color: blue;"><b>{heading} ° </b></span>
    Time: <span style="color: blue;"><b>{time}</b></span>
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
        self.tooltip.setVisible(True)

    def hoverLeaveEvent(self, event):
        # Appeler la méthode parente
        super().hoverLeaveEvent(event)

        # Cacher l'info-bulle
        self.tooltip.setVisible(False)
        self.tooltip_background.setVisible(False)
