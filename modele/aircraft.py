from dataclasses import dataclass, field
from modele.point import Point
from modele.balise import Balise
from modele.utils import rad_to_deg_aero
from modele.collector import Collector

from typing import List, Dict
from copy import deepcopy

import numpy as np

@dataclass(frozen=True)
class Information:
    """ Permet de stocker les informations d'un avion a un instant t donne
    Frozen=True, car non modifiable
    """
    position: Point
    time: float
    speed: float
    heading: float

    def get_position(self): return self.position
    def get_time(self): return self.time
    def get_speed(self): return self.speed
    def get_heading(self, in_aero: bool = True): return rad_to_deg_aero(self.heading)

 
@dataclass
class Aircraft:
    position: Point = field(init=False)
    time: float = field(init=False)
    speed: float
    heading: float = field(init=False)
    flight_plan: List[Balise]
    id: int = field(init=False)  # L'attribut `id` sera défini dans `__post_init__`

    current_target_index: int = field(init=False)  # Indice de la balise cible actuelle
     # Historique des positions de l'avion: key=time et value=Information(position, time, speed, heading)
    history: Dict[float, Information] = field(default_factory=dict, init=False) # Gestion d'un dictionnaire car recherche de point par cle en O(1)
    _is_finished: bool = field(init=False) # La trajectoire est-elle terminee ?

    # Attribut de classe pour suivre le nombre d'instances
    __COUNTER: int = 0

    def __post_init__(self):
        # Incrémenter le compteur de classe et assigner l'ID unique
        self.__class__.__COUNTER += 1
        object.__setattr__(self, 'id', self.__class__.__COUNTER)
        
        # Créer un générateur aléatoire propre à cet avion
        object.__setattr__(self, 'rng', np.random.default_rng(seed=self.id))

        # Initialisation des attributs
        self.current_target_index = 0  # Commence avec la première balise
        self._is_finished = False

        # Premiere position autour de la premiere balise
        self.position = self.generate_position_near_balise(self.flight_plan[self.current_target_index])
        self.time     = 0.
        self.heading  = self.calculate_heading(self.position, self.flight_plan[self.current_target_index])

    def deepcopy(self) -> 'Aircraft':
        new_aircraft = deepcopy(self)
        return new_aircraft

    def has_reached_final_point(self): return self._is_finished

    def generate_position_near_balise(self, balise: Balise) -> Point:
        """
        Génère un objet Point aléatoire dans un rayon défini autour de la balise donnée.
        """
        radius = 0.1 # Rayon maximal autour de la balise (modifiable)
        
        # Générer un angle et une distance aléatoires dans le cercle
        bx, by = balise.getXY()
        if bx < 0.5 and by < 0.5: # Sud Ouest
            min_angle, max_angle = -np.pi/2, np.pi
        elif bx < 0.5 and by >= 0.5: # Nord Ouest
            min_angle, max_angle = np.pi/2, np.pi
        elif bx >= 0.5 and by <= 0.5: # Sud Est
            min_angle, max_angle = -np.pi/2, 0
        else: # Nord Est
            min_angle, max_angle = 0, np.pi/2

        angle    = self.rng.uniform(min_angle, max_angle)
        distance = self.rng.uniform(0, radius)  # Distance entre 0 et le rayon

        # Calculer les coordonnées dans le cercle
        x = bx + distance * np.cos(angle)
        y = by + distance * np.sin(angle)
        z = 0.5 #self.rng.random() # Tirage dans N(0, 1)
        return Point(x, y, z)

    def calculate_heading(self, point: Point, balise: Balise) -> float:
        """ Calcul le heading entre le point et la balise"""
        dx = balise.getX() - point.getX()
        dy = balise.getY() - point.getY()
        heading = np.arctan2(dy, dx) % (2*np.pi) # modulo 2 pi
        return heading


    def update(self, timestep: float) -> None:
        # Sauvegarde la position courante dans l'historique
        info = Information(self.position, self.time, self.speed, self.heading)
        self.history[self.time] = info

        #-----------------------------------------------------------------------
        # Mise a jour des informations
        target_balise = self.flight_plan[self.current_target_index]

        # Calculer la distance vers la balise
        distance_to_target = self.position.distance_horizontale(target_balise)
        approximation = 1.1*self.speed # Pour savoir si on proche de la balise ou pas

        if distance_to_target <= approximation:
            # Passer a la prochaine balise
            if self.current_target_index < len(self.flight_plan) - 1:
                self.current_target_index += 1
                
                target_balise = self.flight_plan[self.current_target_index]
                # Recalculer la distance
                distance_to_target = self.position.distance_horizontale(target_balise)
                self.heading = self.calculate_heading(self.position, target_balise) 

                self.time += timestep
                prev_balise = self.flight_plan[self.current_target_index - 1]
                self.position = Point(prev_balise.x, prev_balise.y, self.position.z)

            else:
                self._is_finished = True
                #print(f"Aircraft {self.id} has reached the final waypoint.")
                return   
        else:
            # Si trajectoire pas terminee
            if not self._is_finished:            
                # Calculer le vecteur de direction vers la balise cible
                dx = abs(target_balise.getX() - self.position.getX())
                dy = abs(target_balise.getY() - self.position.getY())
                dz = 0.

                # Normaliser le vecteur de direction
                direction_x = dx / distance_to_target
                direction_y = dy / distance_to_target
                direction_z = dz / distance_to_target

                # Calculer le déplacement selon la vitesse et le pas de temps
                displacement = self.speed
                new_x = self.position.getX() + np.cos(self.heading) * direction_x * displacement
                new_y = self.position.getY() + np.sin(self.heading) * direction_y * displacement
                new_z = self.position.getZ() + direction_z * displacement

                #print(f"At t={self.time}: {self.position} --> {new_x, new_y, new_z} with heading {self.heading} with speed {self.speed}")
                #print(f"Distance to Target balise: {target_balise}: {distance_to_target}\n")

                # Mettre à jour la position et le temps
                self.position = Point(new_x, new_y, new_z)
                self.time += timestep

    def get_position(self): return self.position
    def get_time(self): return self.time/1000
    def get_speed(self): return self.speed
    def get_heading(self, in_aero=False): 
        if not in_aero: return self.heading
        else: return rad_to_deg_aero(self.heading)
    def get_flight_plan(self): return self.flight_plan
    def get_next_target(self): return self.flight_plan[self.current_target_index]
    def get_id_aircraft(self): return self.id
    def get_history(self): return self.history





class AircraftCollector(Collector):
    def __init__(self, value: Aircraft = None):
        super().__init__()
        if value: self.add(value)
    
    def add_aircraft(self, value: Aircraft) -> None:
        super().add(key = value.get_id_aircraft(), value=value)