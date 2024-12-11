from dataclasses import dataclass, field
from modele.point import Point, PointValue
from modele.balise import Balise
from modele.utils import rad_to_deg_aero
from modele.collector import Collector
from logging_config import setup_logging

from typing import List, Dict, TYPE_CHECKING
from copy import deepcopy

import numpy as np

if TYPE_CHECKING:
    from modele.conflict import Conflict

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
    def get_heading(self, in_aero: bool = True): 
        if in_aero: return rad_to_deg_aero(self.heading)
        else: return self.heading
 
@dataclass
class Aircraft:
    position: Point = field(init=False)
    time: float = field(init=False)
    speed: float
    heading: float = field(init=False)
    flight_plan: List[Balise]
    flight_plan_timed: Dict[str, float] = field(init=False) # Dictionnaire avec le nom de la balise en clé et le temps de passage en valeur
    id: int = field(init=False)  # L'attribut `id` sera défini dans `__post_init__`

    current_target_index: int = field(init=False)  # Indice de la balise cible actuelle
    # Historique des positions de l'avion: key=time et value=Information(position, time, speed, heading)
    history: Dict[float, Information] = field(default_factory=dict, init=False) # Gestion d'un dictionnaire car recherche de point par cle en O(1)
    _is_finished: bool = field(init=False) # La trajectoire est-elle terminee ?
    _conflict_dict: Collector[List[Conflict]] = field(init=False) # Dictionnaire de conflict entre self et les autres: cle=id_autre, valeur=liste des dates conflicts

    # Attribut de classe pour suivre le nombre d'instances
    __COUNTER: int = 0

    def __post_init__(self):
        self.logger = setup_logging(__class__.__name__)

        # Incrémenter le compteur de classe et assigner l'ID unique
        self.__class__.__COUNTER += 1
        object.__setattr__(self, 'id', self.__class__.__COUNTER)
        
        # Créer un générateur aléatoire propre à cet avion
        object.__setattr__(self, 'rng', np.random.default_rng(seed=self.id))

        # Initialisation des attributs
        self.current_target_index = 0  # Commence avec la première balise
        self._is_finished = False
        self.flight_plan_timed = {}

        # Premiere position autour de la premiere balise
        self.position = self.generate_position_near_balise(self.flight_plan[self.current_target_index])
        self.time     = 0.
        self.heading  = self.calculate_heading(self.position, self.flight_plan[self.current_target_index])

        # Enregistrer les temps de passage prévu par le plan de vol
        self.flight_plan_timed = {} # Initialisation du dictionnaire rempli par calculate_estimated_times
        self.calculate_estimated_times()

        self._conflict_dict = Collector() # Dictionnaire vide au depart
        
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
    
    def calculate_estimated_times(self) -> None:
        """
        Calcule les temps estimés de passage de l'avion pour chaque balise.
        Le Range dans l'attribut flight_time_timed
        """
        current_position = self.position
        current_time = self.time

        for balise in self.flight_plan[self.current_target_index:]:
            distance_to_balise = current_position.distance_horizontale(balise)
            time_to_balise = distance_to_balise / self.speed
            current_time += time_to_balise
            self.flight_plan_timed[balise.get_name()] = round(current_time, 2)
            current_position = balise  # Simuler que l'avion atteint la balise
            print(self.id, balise, self.flight_plan_timed[balise.get_name()] )
        return None


    def update(self, timestep: float) -> None:
        # Sauvegarde la position courante dans l'historique
        info = Information(self.position, self.time, self.speed, self.heading)
        self.history[self.time] = info

        #-----------------------------------------------------------------------
        # Mise a jour des informations
        target_balise = self.flight_plan[self.current_target_index]

        # Calculer la distance vers la balise
        distance_to_target = self.position.distance_horizontale(target_balise)
        approximation = 1.1 * self.speed * timestep # Pour savoir si on proche de la balise ou pas
        
        if distance_to_target <= approximation:
            # Passer à la balise suivante
            if self.current_target_index < len(self.flight_plan) - 1:
                self.current_target_index += 1
                target_balise = self.flight_plan[self.current_target_index]
                self.heading = self.calculate_heading(self.position, target_balise)
                self.time += timestep
            else:
                self._is_finished = True
                #print(f"Aircraft {self.id} has reached the final waypoint.")
                return
        else:
            # Déplacement rectiligne vers la balise
            displacement = self.speed * timestep

            # Calculer les nouvelles coordonnées
            direction_x = (target_balise.x - self.position.x) / distance_to_target
            direction_y = (target_balise.y - self.position.y) / distance_to_target
            direction_z = 0.0  # Pas de variation verticale pour l'instant

            new_x = self.position.x + direction_x * displacement
            new_y = self.position.y + direction_y * displacement
            new_z = self.position.z + direction_z * displacement

            #print(f"At t={self.time}: {self.position} --> {new_x, new_y, new_z} with heading {self.heading} with speed {self.speed}")
            #print(f"Distance to Target balise: {target_balise}: {distance_to_target}\n")

            # Mettre à jour la position et le temps
            self.position = self.controle_position(new_x, new_y, new_z)
            self.time += timestep

    def controle_position(self, x: float, y: float, z:float):
        try:
            new_point = Point(x, y, z)
        except ValueError:
            if x < PointValue.MinX or x > PointValue.MaxX:
                self.heading = np.pi - self.heading
            if y < PointValue.MinY or y > PointValue.MaxY:
                self.heading = -self.heading
            if self.heading < 0:
                self.heading += 2*np.pi
            if self.heading > 2*np.pi:
                self.heading -= 2*np.pi    

            new_point = self.position
        finally:
            return new_point        

    def get_position(self): return self.position
    def get_time(self): return self.time
    def get_speed(self): return self.speed
    def get_heading(self, in_aero: bool = False): 
        if in_aero: return rad_to_deg_aero(self.heading)
        else: return self.heading
    def get_flight_plan(self): return self.flight_plan
    def get_next_target(self): return self.flight_plan[self.current_target_index]
    def get_id_aircraft(self): return self.id
    def get_history(self): return self.history

    def set_speed(self, speed: float) -> None:
        self.speed = speed
    
    def set_heading(self, hdg: float) -> None:
        self.heading = hdg

    def get_flight_plan_timed(self) -> Dict[str, float]: return self.flight_plan_timed

    def is_in_conflict(self) -> bool: return not self._conflict_dict.is_empty() # Si collection vide alors pas de conflit

    def get_conflicts(self) -> Collector[List[Conflict]]: return self._conflict_dict
    
    def set_conflicts(self, conflict_info: Conflict) -> None:
        """ 
            Methode qui ajoute le conflict au dictionnaire.
        """
        # Ajout du conflict dans le dictionnaire
        conflict_with = conflict_info.get_aircraft_two().get_id_aircraft()
        values = self._conflict_dict.get_from_key(conflict_with)

        self.logger.info(f"Ajout d'un conflict: {conflict_info}")

        if values: # La cle existe si ca renvoie pas None
            self._conflict_dict.get_from_key(conflict_with).append(conflict_info) # Modification en place
        else:
            self._conflict_dict.add(key=conflict_with, value=[conflict_info]) # Forcer la valeur a etre une liste



class AircraftCollector(Collector):
    def __init__(self, value: Aircraft = None):
        super().__init__()
        if value: self.add(value)
    
    def add_aircraft(self, value: Aircraft) -> None:
        super().add(key = value.get_id_aircraft(), value=value)