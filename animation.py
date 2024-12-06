from matplotlib.pyplot import Axes
from matplotlib.patches import RegularPolygon
import numpy as np

from typing import List
from aircraft import Aircraft
from balise import DatabaseBalise
from route import Airway
from sector import Sector


def update(frame: int, aircrafts: List[Aircraft], timestep: float, ax: Axes, 
           main_sector: Sector, secondary_sector: Sector, balises: DatabaseBalise, 
           routes: Airway):
    """
    Met à jour la position des avions et redessine la figure à chaque frame.
    
    :param frame: Le numéro du frame actuel.
    :param aircrafts: Liste des avions à animer.
    :param timestep: Le pas de temps pour l'animation.
    :param ax: L'axe de la figure sur lequel dessiner.
    :param main_sector: Le secteur principal à dessiner.
    :param secondary_sector: Le secteur secondaire à dessiner.
    :param balises: Liste des balises à dessiner.
    :param routes: Routes aériennes à dessiner.
    """
    ax.clear()  # Effacer la figure à chaque frame pour redessiner
    limit_xy = 0.05  # Limite d'affichage autour de la zone [0, 1]

    # Affichage des éléments statiques : secteurs, balises, et routes
    ax = main_sector.plot(ax, color="#D9EAD3")  # Secteur principal
    ax = secondary_sector.plot(ax, color="#F3F3D9")  # Secteurs secondaires
    ax = balises.plot(ax, color='#BBBBBB')  # Balises
    ax = routes.plot(ax, balises, color='grey')  # Routes aériennes

    # Met à jour les avions et dessine leurs nouvelles positions
    triangle_size = 0.01  # Taille du triangle
    for aircraft in aircrafts:
        aircraft.update(timestep)  # Mise à jour de la position de l'avion
        print(aircraft.id, aircraft.has_reached_final_point())
        if not aircraft.has_reached_final_point():
            # Dessiner les positions precedantes sur la carte
            history = aircraft.history
            if len(history) > 1:
                N_PAST = 50
                timesteps = sorted(history.keys(), reverse=True)  # Tri des temps dans l'ordre décroissant

                for i, t in enumerate(timesteps[:N_PAST]):
                    if i % 4 == 0:
                        oldinfo = history.get(t)
                        oldpost = oldinfo.position
                        
                        # Couleur et taille des marqueurs
                        alpha = 1 - (i + 1) / N_PAST  # Alpha décroît avec l'index
                        marker_size = min(6, 12 * (1 - (i+1)/N_PAST))
                        
                        # Afficher le point
                        ax.plot(oldpost.x, oldpost.y, color='black', marker=".", ms=marker_size, alpha=alpha)

            # Dessiner la position de l'avion sur la carte
            # Ajouter un triangle orienté selon le heading
            triangle_size = 0.01  # Taille du triangle
            triangle = RegularPolygon(
                (aircraft.position.x, aircraft.position.y),  # Position du centre
                numVertices=3,                               # Nombre de sommets (triangle)
                radius=triangle_size,                        # Taille
                orientation=aircraft.heading - np.pi / 2,    # Orientation alignée avec le cap
                color="black"                                # Couleur
            )
            ax.add_patch(triangle)
            #ax.plot(aircraft.position.x, aircraft.position.y, 'black', marker="o", ms=8)


    # Réglages de l'axe et de la vue
    ax.set_xlim(-limit_xy, 1 + limit_xy)
    ax.set_ylim(-limit_xy, 1 + limit_xy)
    ax.set_aspect('equal', adjustable='box')

    return ax,