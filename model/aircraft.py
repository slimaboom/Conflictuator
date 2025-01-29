from dataclasses import dataclass, field
from model.point import Point, PointValue
from model.balise import Balise
from utils.conversion import rad_to_deg_aero
from model.collector import Collector
from logging_config import setup_logging
from algorithm.storage import DataStorage

from typing import List, Dict, TYPE_CHECKING, Optional
from copy import deepcopy
from weakref import WeakSet
from enum import Enum

import numpy as np
import pdb

if TYPE_CHECKING:
    from model.conflict_manager import ConflictManager, ConflictInformation

class SpeedValue(Enum):
    MAX: float = 1e-2
    MIN: float = 1e-4
    STEP: float = 1e-4


@dataclass(frozen=True)
class Information:
    """ Permet de stocker les informations d'un avion a un instant t donne
    Frozen=True, car non modifiable
    """
    position: Point
    time: float
    speed: float
    heading: float
    take_off: float
    flight_time: float

    def get_position(self): return self.position
    def get_time(self): return self.time
    def get_speed(self): return self.speed
    def get_heading(self, in_aero: bool = True): 
        if in_aero: return rad_to_deg_aero(self.heading)
        else: return self.heading
    def get_take_off_(self): return self.take_off
    def get_flight_time(self): return self.flight_time


@dataclass
class Aircraft:
    speed: float
    flight_plan: List[Balise]

    position: Point = field(init=False)
    time: float = field(init=False)
    flight_time: float = field(init=False)
    take_off_time: Optional[float] = 0.

    heading: float = field(init=False)
    flight_plan_timed: Dict[str, float] = field(init=False) # Dictionnaire avec le nom de la balise en clé et le temps de passage en valeur
    id: int = field(init=False)  # L'attribut `id` sera défini dans `__post_init__`
    rng: np.random.Generator = field(init=False)
    
    current_target_index: int = field(init=False)  # Indice de la balise cible actuelle
    # Historique des positions de l'avion: key=time et value=Information(position, time, speed, heading)
    history: Dict[float, Information] = field(default_factory=dict, init=False) # Gestion d'un dictionnaire car recherche de point par cle en O(1)
    _is_finished: bool = field(init=False) # La trajectoire est-elle terminee ?
    _conflict_dict: Collector[List['ConflictInformation']] = field(init=False) # Dictionnaire de conflict entre self et les autres: cle=id_autre, valeur=liste des dates conflicts
    
    commands: List[DataStorage] = field(init=False)
    next_command: DataStorage = field(init=False)

    # Attribut de classe pour suivre le nombre d'instances
    __COUNTER: int = 0

    _observers: WeakSet = None

    def __hash__(self):
        return hash(self.get_id_aircraft())

    def __eq__(self, other):
        if not isinstance(other, Aircraft):
            return False
        return self.get_id_aircraft() == other.get_id_aircraft()


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
        self.flight_time = 0.

        object.__setattr__(self, 'heading',  self.calculate_heading(self.position, self.flight_plan[self.current_target_index]))

        # Enregistrer les temps de passage prévu par le plan de vol
        self.flight_plan_timed = {} # Initialisation du dictionnaire rempli par calculate_estimated_times_commands

        self._conflict_dict = Collector() # Dictionnaire vide au depart
        self.commands = [DataStorage(id=self.id, time=self.take_off_time,
                                     speed=self.speed, heading=self.heading)
                        ]
        
        self.next_command = self.set_next_command()
        self.calculate_estimated_times_commands()

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
        z = 0.5 #np.round(self.rng.random(), 3) # Tirage dans N(0, 1)
        return Point(x, y, z)

    def calculate_heading(self, point: Point, balise: Balise) -> float:
        """ Calcul le heading entre le point et la balise"""
        dx = balise.getX() - point.getX()
        dy = balise.getY() - point.getY()
        heading = np.arctan2(dy, dx) % (2*np.pi) # modulo 2 pi
        return heading
    
    def calculate_estimated_times_commands(self) -> None:
        """
        Calcule les temps estimés de passage de l'avion pour chaque balise avec un pas adaptatif.
        Le pas de temps devient plus petit à l'approche des balises ou d'un changement de vitesse.
        """
        if len(self.history) <= 0:  # L'avion n'a pas encore bougé.
            current_position = self.position
            current_time = self.take_off_time
            current_speed = self.speed
            current_command_index = 0
            current_command = self.commands[current_command_index] if self.commands else None
            current_flight_time = 0.

            # Initialisation des temps pour les balises
            self.flight_plan_timed = {}

            for balise in self.flight_plan:
                while True:
                    # Distance horizontale jusqu'à la balise
                    distance_to_balise = current_position.distance_horizontale(balise)

                    # Temps jusqu'au changement de vitesse (si applicable)
                    time_to_next_command = (
                        current_command.time - current_time
                        if current_command and current_command.time > current_time
                        else float('inf')
                    )

                    # Choix d'un pas adaptatif en fonction de la distance et du temps restant
                    if distance_to_balise > 10 * self.speed and time_to_next_command > 10:  # Balise non atteinte avec un pas de 10 ou prochaine commandes dans plus de 10 sec
                        time_step = 10
                    elif distance_to_balise > self.speed or time_to_next_command > 1:  #  Balise non atteinte avec un pas de 1 ou prochaine commandes dans plus de 1 sec
                        time_step = 1
                    elif distance_to_balise > 0.1 * self.speed or time_to_next_command > 0.1:   #Balise non atteinte avec un pas de .1 ou prochaine commandes dans plus de .1 sec
                        time_step = 0.1
                    else:  # Très proche d'une balise ou d'un changement de vitesse
                        time_step = 0.01

                    # Vérifier si la balise est atteinte avec ce pas
                    if distance_to_balise <= current_speed * time_step:
                        # Balise atteinte
                        dt = distance_to_balise / current_speed
                        current_time += distance_to_balise / current_speed
                        current_position = Point(balise.getX(), balise.getY(), current_position.getZ())
                        self.flight_plan_timed[balise.get_name()] = self.__round(current_time)
                        current_flight_time += dt
                        break
                    else:
                        # Sinon, avancer d'un pas de temps
                        current_time += time_step
                        proportion = (current_speed * time_step) / distance_to_balise
                        inter_x = current_position.getX() + proportion * (balise.getX() - current_position.getX())
                        inter_y = current_position.getY() + proportion * (balise.getY() - current_position.getY())
                        inter_z = current_position.getZ()  # Altitude inchangée
                        current_position = Point(inter_x, inter_y, inter_z)
                        current_flight_time += time_step

                    # Gérer les commandes de vitesse
                    if current_command and current_time >= current_command.time:
                        current_speed = current_command.speed
                        current_command_index += 1
                        current_command = (
                            self.commands[current_command_index]
                            if current_command_index < len(self.commands)
                            else None
                        )



    def clear_flight_plan_timed(self):
        return {k:v for k, v in self.get_flight_plan_timed().items() if v < self.time}

    def update(self, timestep: float) -> None:
        #-----------------------------------------------------------------------
        if self.time < self.take_off_time:
            self.time += timestep # incrementer le temps
        else:   #self.time >= self.take_off_time
            # Sauvegarde la position courante dans l'historique
            self.time = self.__round(self.time)
            info = Information(self.position, 
                               self.time, 
                               self.speed, 
                               self.heading, 
                               self.take_off_time, 
                               self.__round(self.flight_time)
                               )
            self.history[self.time] = info
            
            self.time += timestep

            #Vérifier si on doit faire une commande et la faire si besoin
            if self.id > 0 :
                self.check_commands()

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
                    self.flight_time += timestep
                else:
                    self._is_finished = True
                    #TO DO on continue en ligne droite jusqu'a sortie du secteur 
                    #print(f"Aircraft {self.id} has reached the final waypoint.")
                    return
            else:
                # Déplacement rectiligne vers la balise
                displacement = self.speed * timestep

                # Calculer les nouvelles coordonnées
                direction_z = 0.0  # Pas de variation verticale pour l'instant

                new_x = self.position.getX() + displacement * np.cos(self.heading)
                new_y = self.position.getY() + displacement * np.sin(self.heading)
                new_z = self.position.getZ() + displacement * direction_z

                # Mettre à jour la position et le temps
                self.position = self.controle_position(new_x, new_y, new_z)
                self.flight_time += timestep

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
    def set_time(self, time: float) -> None: 
        self.time = time
    def get_flight_time(self): return self.flight_time
    def get_take_off_time(self): return self.take_off_time
    def get_speed(self): return self.speed
    def get_heading(self, in_aero: bool = False): 
        if in_aero:return rad_to_deg_aero(self.heading)
        else: return self.heading
    def get_flight_plan(self): return self.flight_plan
    def get_next_target(self): return self.flight_plan[self.current_target_index]
    def get_id_aircraft(self): return self.id
    def get_history(self): return self.history
    def get_random_generator(self): return self.rng
    def set_aircraft_id(self, id: int) -> None:
        self.id = id
        

    def set_speed(self, speed: float) -> None:
        """ Modifie la vitesse de l'avion et recalcul les conflits futurs """
        self.speed = speed
    
    def set_heading(self, hdg: float) -> None:
        #self.__class__.logger.info(f"Set heading to aircraft {self.id}: from {self.heading} to {hdg}")
        self.heading = hdg

    def set_take_off_time(self, take_off_time: float) -> None:
        self.take_off_time = take_off_time

    def get_flight_plan_timed(self) -> Dict[str, float]: return self.flight_plan_timed

    def is_in_conflict(self) -> bool: return not(self._conflict_dict == {})

    def get_conflicts(self) -> Collector[List['ConflictInformation']]: return self._conflict_dict
   
    def clear_conflicts(self, with_aircraft_id: int = None) -> None:
        """Efface les conflits dépassés ou spécifiques à un autre avion."""
        # Nouveau Collector pour stocker les conflits a garder
        #self.logger.info(f"Nettoyage des conflicts de l'avion {self.get_id_aircraft()} with_aircraft_id={with_aircraft_id})")
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
            #self.logger.info(f"filtered_conflicts pour avion {self.id}: {filtered_conflicts}")
            # Ajouter les conflits restants dans le nouveau collector
            if filtered_conflicts:
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

        #self.logger.info(f"Ajout d'un conflict: {conflict_info}: {values}")

        if values: # La cle existe si ca renvoie pas None
            if not conflict_info in values:
                self._conflict_dict.get_from_key(conflict_with).append(conflict_info) # Modification en place
        else:
            self._conflict_dict.add(key=conflict_with, value=[conflict_info]) # Forcer la valeur a etre une liste


    def update_conflicts(self):
        """ Recalcul les conflits posterieurs a la date courante"""
        
        # Recalculer le plan de vol
        self.flight_plan_timed = self.clear_flight_plan_timed()
        self.calculate_estimated_times_commands()
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


    def get_position_from_time(self, time: float) -> Point:
        """ Renvoie la position de l'avion au temps <time>"""
        return self.__find_position_position(time=time)

    def __find_position_position(self, target_time: float) -> Point:

        if target_time < self.take_off_time:
            raise ValueError("The requested time is before the aircraft's takeoff time.")

        current_position = self.position
        current_time = self.take_off_time
        current_speed = self.speed

        for balise in self.flight_plan:
            balise_time = self.flight_plan_timed[balise.get_name()]

            for command in self.commands:
                if command.time and current_time < command.time < balise_time:
                    
                    time_to_command = command.time - current_time
                    proportion = time_to_command * current_speed / (balise_time - current_time)
                    new_x = current_position.getX() + proportion * (balise.getX() - current_position.getX())
                    new_y = current_position.getY() + proportion * (balise.getY() - current_position.getY())
                    new_z = current_position.getZ() + proportion * (balise.getZ() - current_position.getZ())
                    current_position = Point(new_x, new_y, new_z)

                    current_time = command.time
                    current_speed = command.speed

            if current_time <= target_time <= balise_time:
                remaining_time = target_time - current_time
                proportion = remaining_time * current_speed / (balise_time - current_time)
                final_x = current_position.getX() + proportion * (balise.getX() - current_position.getX())
                final_y = current_position.getY() + proportion * (balise.getY() - current_position.getY())
                final_z = current_position.getZ() + proportion * (balise.getZ() - current_position.getZ())
                return Point(final_x, final_y, final_z)

            current_position = balise
            current_time = balise_time

        return current_position
    
    def set_next_command(self) -> Optional[DataStorage]:
        "renvoie la prochiane commands a appliqué "
        if not self.commands:  # Si aucune commande n'est définie
            return None

        # Rechercher la première commande dont le temps est supérieur à l'heure actuelle
        next_command = next((cmd for cmd in self.commands if (cmd.time > self.time and cmd.time > self.take_off_time)), None)
        return next_command

    
    def set_commands(self, commands: List[DataStorage]) -> None:
        """ Set la liste de commande a l'avion (DataStorage) et recalcule les conflit en consequence"""
        if commands:
            commands.sort(key= lambda c: c.time)
            self.commands = commands
            
            if self.commands:
                cmd = commands[0]
                self.set_take_off_time(cmd.time)
                self.set_speed(cmd.speed)
                self.set_heading(cmd.heading)

        # Recalculer les conflicts
        self.update_conflicts()

    def add_command(self, command: DataStorage):
        # Ajouter une commande ie. un changement de vitesse ou de cap
        self.commands.append(command)
        self.commands.sort(key=lambda c: c.time)  # On s'assure que c'est trier en t croissant

    def check_commands(self):

        if self.next_command is None:
            self.next_command = self.set_next_command()

        # Exécuter la commande si elle est arrivée à échéance
        if self.next_command and self.next_command.time <= self.time:
            self.set_speed(self.next_command.speed)  # Appliquer le changement de vitesse
            print(f"Speed : {self.speed} à time {self.next_command.time} for aircraft {self.id}")
            #self.commands.remove(self.next_command)  # Retirer la commande exécutée
            self.next_command = None  # Réinitialiser pour trouver la suivante

    def get_commands(self):
        return self.commands

    def __round(self, value: float) -> float:
        return round(value, 2)


class AircraftCollector(Collector[Aircraft]):
    def __init__(self, value: Aircraft = None):
        super().__init__()
        if value: self.add(value)
    
    def add_aircraft(self, value: Aircraft) -> None:
        super().add(key = value.get_id_aircraft(), value=value)