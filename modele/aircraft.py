from dataclasses import dataclass, field
from modele.point import Point, PointValue
from modele.balise import Balise
from modele.utils import rad_to_deg_aero
from modele.collector import Collector
from logging_config import setup_logging

from typing import List, Dict, TYPE_CHECKING
from copy import deepcopy
from weakref import WeakSet

import numpy as np

if TYPE_CHECKING:
    from modele.conflict_manager import ConflictManager, ConflictInformation

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
    _conflict_dict: Dict[int, List['ConflictInformation']] = field(init=False) # Dictionnaire de conflict entre self et les autres: cle=id_autre, valeur=liste des dates conflicts

    # Attribut de classe pour suivre le nombre d'instances
    __COUNTER: int = 0

    _observers: WeakSet = None

    def __post_init__(self):
        self.__class__.logger = setup_logging(__class__.__name__)

        # Incrémenter le compteur de classe et assigner l'ID unique
        self.__class__.__COUNTER += 1
        object.__setattr__(self, 'id', self.__class__.__COUNTER)
        
        # Créer un générateur aléatoire propre à cet avion
        object.__setattr__(self, 'rng', np.random.default_rng(seed=self.id))

        # Initialiser les observateurs au niveau de la classe, si ce n'est pas encore fait
        if self.__class__._observers == None:
            self.__class__._observers = WeakSet()

        # Initialisation des attributs
        self.current_target_index = 0  # Commence avec la première balise
        self._is_finished = False
        self.flight_plan_timed = {}

        # Premiere position autour de la premiere balise
        self.position = self.generate_position_near_balise(self.flight_plan[self.current_target_index])
        self.time     = 0.
        object.__setattr__(self, 'heading',  self.calculate_heading(self.position, self.flight_plan[self.current_target_index]))

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

    def clear_flight_plan_timed(self):
        return {k:v for k, v in self.get_flight_plan_timed().items() if v < self.time}

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
            dx = target_balise.getX() - self.position.getX()
            dy = target_balise.getY() - self.position.getY()
            direction_x = dx/ distance_to_target
            direction_y = dy / distance_to_target
            direction_z = 0.0  # Pas de variation verticale pour l'instant

            new_x = self.position.getX() + displacement * np.cos(self.heading)
            new_y = self.position.getY() + displacement * np.sin(self.heading)
            new_z = self.position.getZ() + displacement * direction_z

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
        """ Modifie la vitesse de l'avion et recalcul les conflits futurs """
        self.speed = speed

        # Recalculer les conflicts
        self.update_conflicts()
    
    def set_heading(self, hdg: float) -> None:
        self.__class__.logger.info(f"Set heading to aircraft {self.id}: from {self.heading} to {hdg}")
        self.heading = hdg

    def get_flight_plan_timed(self) -> Dict[str, float]: return self.flight_plan_timed

    def is_in_conflict(self) -> bool: return not self._conflict_dict.is_empty() # Si collection vide alors pas de conflit

    def get_conflicts(self) -> Collector[List['ConflictInformation']]: return self._conflict_dict
   
    def clear_conflicts(self, with_aircraft_id: int = None) -> None:
        """Efface les conflits dépassés ou spécifiques à un autre avion."""
        # Nouveau Collector pour stocker les conflits a garder
        self.logger.info(f"Nettoyage des conflicts de l'avion {self.get_id_aircraft()} with_aircraft_id={with_aircraft_id})")
        new_collector = Collector()

        for key, conflicts in self._conflict_dict.get_all().items():
            # Filtrer les conflits selon la condition
            filtered_conflicts = [
                c for c in conflicts
                if (with_aircraft_id == None and c.get_conflict_time_one() < self.time) or
                   (with_aircraft_id != None and (
                       c.get_aircraft_two().get_id_aircraft() != with_aircraft_id or 
                       c.get_conflict_time_one() < self.time))
            ]
            self.logger.info(f"filtered_conflicts pour avion {self.id}: {filtered_conflicts}")
            # Ajouter les conflits restants dans le nouveau collector
            new_collector.add(key, filtered_conflicts)

        # Remplacer l'ancien _conflict_dict par le nouveau
        self._conflict_dict = new_collector

    def set_conflicts(self, conflict_info: 'ConflictInformation') -> None:
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

    def update_conflicts(self):
        """ Recalcul les conflits posterieurs a la date courante"""
        # Recalculer le plan de vol
        self.flight_plan_timed = self.clear_flight_plan_timed()
        self.calculate_estimated_times()

        # Effacer tous les conflicts de self
        self.clear_conflicts()

        # Recalculer les conflicts
        Aircraft.notify_observers(self)

    @classmethod
    def register_observer(cls, observer: 'ConflictManager'):
        """Enregistre un observateur global (ex: ConflictManager)."""
        cls._observers.add(observer)

    @classmethod
    def notify_observers(cls, aircraft: 'Aircraft'):
        """Notifier les observateurs d'un changement dans un avion."""
        for observer in cls._observers:
            observer.update_aircraft_conflicts(aircraft)


class AircraftCollector(Collector):
    def __init__(self, value: Aircraft = None):
        super().__init__()
        if value: self.add(value)
    
    def add_aircraft(self, value: Aircraft) -> None:
        super().add(key = value.get_id_aircraft(), value=value)