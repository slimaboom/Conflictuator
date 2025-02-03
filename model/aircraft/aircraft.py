from dataclasses import dataclass, field
from model.aircraft. information import Information
from model.point import Point, PointValue
from model.balise import Balise
from utils.conversion import rad_to_deg_aero
from model.collector import Collector
from logging_config import setup_logging
from model.aircraft.storage import DataStorage

from typing import List, Dict, TYPE_CHECKING, Optional
from copy import deepcopy
from weakref import WeakSet

import numpy as np

if TYPE_CHECKING:
    from model.conflict_manager import ConflictManager, ConflictInformation

class Aircraft:
    __REGISTRY: Dict[int, 'Aircraft'] = {}
    __observers: WeakSet = WeakSet()

    def __init__(self, flight_plan: List[Balise], speed: float, id: int = None, take_off_time=0.):
        # Logger
        self.logger = setup_logging(self.__class__.__name__)

        self.flight_plan       = flight_plan
        
        # Initialisation du dictionnaire rempli par calculate_estimated_times_commands
        self.flight_plan_timed = {}

        if speed == None or speed <= 0: # Protection pour calcul des temps de passage au balise !!!
            error = f"{self.__class__.__name__} cannot be instanciate due to speed negative or null value or None value"
            raise ValueError(error)
        
        if take_off_time < 0:
            error = f"{self.__class__.__name__} cannot be instanciate due to speed negative value for take_off_time: must be >=0"
            raise error
        
        # Vitesse
        self.speed = speed

        # Identifiant
        self.id = id if id != None else len(self.get_available_aircrafts()) + 1

        # Generateur de nombre aleatoire
        self.rng = np.random.default_rng(seed=self.id)
        
        # Initialisation des attributs
        self.current_target_index = 0  # Commence avec la première balise
        self._is_finished         = False
        self.flight_plan_timed    = {}

        # Premiere position autour de la premiere balise
        self.start_position = self.generate_position_near_balise(self.flight_plan[self.current_target_index])
        self.position       = deepcopy(self.start_position)
        self.time           = 0.
        self.flight_time    = 0.
        self.take_off_time  = take_off_time

        # Historique des positions
        self.history: Dict[float, 'Information'] = {}

        # Cap entre la première position et la balise
        self.heading = self.calculate_heading(self.position, self.flight_plan[self.current_target_index])

        # Collecteur de conflicts
        self._conflict_dict = Collector(List['ConflictInformation']) # Collecteur vide au depart
        # List de commandes de l'avion
        # Si l'avion doit changer de vitesse dans le temps par exemple.
        self.commands = [DataStorage(id=self.id, time=self.take_off_time,
                                     speed=self.speed, heading=self.heading)
                        ]
        
        # Prochaine commande à appliquer
        self.next_command = self.set_next_command()

        # Calcul du plan de vol timé par rapport à la vitesse (et au commande dans le temps)
        self.calculate_estimated_times_commands()

        self.__REGISTRY[self.id] = self


    @classmethod
    def reinititalise_registry(cls) -> None:
        """Nettoie le dictionnaire des instances des avions disponibles en le vidant"""
        cls.__REGISTRY.clear()
    
    @classmethod
    def get_available_aircrafts(cls) -> Dict[int, 'Aircraft']:
        """Renvoie le dictionnaire des instances des avions disponibles"""
        return cls.__REGISTRY

    @classmethod
    def remove_aircraft_from_registry(cls, aircraft: 'Aircraft') -> None:
        """Supprime l'aircraft du registre de classe Aircraft"""
        id = aircraft.get_id_aircraft()
        if id in cls.__REGISTRY.keys():
            del cls.__REGISTRY[aircraft.get_id_aircraft()]

    @classmethod
    def register_observer(cls, observer: 'ConflictManager'):
        """Enregistre un observateur global (ex: ConflictManager)."""
        cls.__observers.add(observer)

    @classmethod
    def notify_observers(cls, aircraft: 'Aircraft'):
        """Notifier les observateurs d'un changement dans un avion."""
        for observer in cls.__observers:
            observer.update_aircraft_conflicts(aircraft)

    def __hash__(self):
        return hash(self.get_id_aircraft())

    def __eq__(self, other):
        if not isinstance(other, Aircraft):
            return False
        return self.get_id_aircraft() == other.get_id_aircraft()


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

    def get_conflicts(self) -> Collector[List['ConflictInformation']]: return self._conflict_dict
    def get_commands(self) -> List['DataStorage']: return self.commands

    def set_speed(self, speed: float) -> None:
        """ Modifie la vitesse de l'avion et recalcul les conflits futurs """
        self.speed = speed
    
    def set_heading(self, hdg: float) -> None:
        #self.__class__.logger.info(f"Set heading to aircraft {self.id}: from {self.heading} to {hdg}")
        self.heading = hdg

    def set_take_off_time(self, take_off_time: float) -> None:
        self.take_off_time = take_off_time

    def get_flight_plan_timed(self) -> Dict[str, float]: return self.flight_plan_timed

    def is_in_conflict(self) -> bool: return not(self._conflict_dict.is_empty())


    def get_arrival_time_on_last_point(self) -> float:
        """Renvoie le temps de passage à la dernière balise du plan de vol"""
        # Heure d'arrivée au dernier point du plan de vol de l'avion
        last_time = list(self.get_flight_plan_timed().values())[-1]
    
        # Retourner la durée maximale
        return last_time # 0.0 si aucune donnée n'est présente
    
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
            # Trier par ordre d'arriver mais normalement si le calcul est bien, il n'y a pas besoin
            # car ca changerait le plan de vol !
            #self.flight_plan_timed = dict(sorted(self.flight_plan_timed.items(), 
            #                                     key=lambda item: item[1]
            #                                     )
            #                              )


    def clear_flight_plan_timed(self):
        return {k:v for k, v in self.get_flight_plan_timed().items() if v < self.time}


    def update(self, timestep: float) -> None:
        """Mise à jour des attributs de l'avion pour le faire avancer en utilisant get_position_from_time"""
        self.time     = self.__round(self.time + timestep)
        self.position = self.get_position_from_time(time=self.time)

    # def update(self, timestep: float) -> None:
    #    """Method de mise à jour des attributs de l'avion pour le faire avancer.
    #        Utiliser du début du projet SITA-IA 22 jusqu'au 30/01/2025 17:08'
    #    """
    #     #-----------------------------------------------------------------------
    #     if self.time < self.take_off_time:
    #         self.time += timestep # incrementer le temps
    #     else:   #self.time >= self.take_off_time
    #         # Sauvegarde la position courante dans l'historique
    #         self.time = self.__round(self.time)
    #         info = Information(self.position, 
    #                            self.time, 
    #                            self.speed, 
    #                            self.heading, 
    #                            self.take_off_time, 
    #                            self.__round(self.flight_time)
    #                            )
    #         self.history[self.time] = info
            
    #         self.time += timestep

    #         #Vérifier si on doit faire une commande et la faire si besoin
    #         if self.id > 0 :
    #             self.check_commands()

    #         # Mise a jour des informations
    #         target_balise = self.flight_plan[self.current_target_index]

    #         # Calculer la distance vers la balise
    #         distance_to_target = self.position.distance_horizontale(target_balise)
    #         approximation = 1.1 * self.speed * timestep # Pour savoir si on proche de la balise ou pas
            
    #         if distance_to_target <= approximation:
    #             # Passer à la balise suivante
    #             if self.current_target_index < len(self.flight_plan) - 1:
    #                 self.current_target_index += 1
    #                 target_balise = self.flight_plan[self.current_target_index]
    #                 self.heading = self.calculate_heading(self.position, target_balise)
    #                 self.flight_time += timestep
    #             else:
    #                 self._is_finished = True
    #                 #TO DO on continue en ligne droite jusqu'a sortie du secteur 
    #                 #print(f"Aircraft {self.id} has reached the final waypoint.")
    #                 return
    #         else:
    #             # Déplacement rectiligne vers la balise
    #             displacement = self.speed * timestep

    #             # Calculer les nouvelles coordonnées
    #             direction_z = 0.0  # Pas de variation verticale pour l'instant

    #             new_x = self.position.getX() + displacement * np.cos(self.heading)
    #             new_y = self.position.getY() + displacement * np.sin(self.heading)
    #             new_z = self.position.getZ() + displacement * direction_z

    #             # Mettre à jour la position et le temps
    #             self.position = self.controle_position(new_x, new_y, new_z)
    #             self.flight_time += timestep

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


    def clear_conflicts(self, with_aircraft_id: int = None) -> None:
        """Efface les conflits dépassés ou spécifiques à un autre avion."""
        # Nouveau Collector pour stocker les conflits a garder
        #self.logger.info(f"Nettoyage des conflicts de l'avion {self.get_id_aircraft()} with_aircraft_id={with_aircraft_id})")
        new_collector = Collector()
        for key, conflicts in self.get_conflicts().get_all().items():
            if conflicts != None:
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


    def update_conflicts(self, recalcul = True, dt:int = 0):
        """ Recalcul les conflits posterieurs a la date courante"""
        if recalcul:
            # Recalculer le plan de vol
            #self.flight_plan_timed = self.clear_flight_plan_timed()
            self.calculate_estimated_times_commands()
        elif dt != 0: 
            self.flight_plan_timed_delayed(dt)
        # Effacer tous les conflicts de self
        self.clear_conflicts()

        # Recalculer les conflicts
        Aircraft.notify_observers(self)
    
    def flight_plan_timed_delayed(self, dt : int) -> None:
        for time in self.flight_plan_timed.values():
            time += dt
        return None


    def get_position_from_time(self, time: float) -> Point:
        """ Renvoie la position de l'avion au temps <time>"""
        return self.__find_next_position(target_time=time)

    def __find_next_position(self, target_time: float) -> Point:
        """Methode qui calcul par interpolation linéaire sa position 
        en fonction de la cible temporelle passéé en paramètre
        
        /!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\
        /!\     Cette méthode est très sensibe au modification !!!        /!\
        /!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\/!\
        """
        def find_keys(flight_plan_timed: Dict[str, float], time: float):
            """Chercher entre quelle balise l'avion est en fonction du time"""
            # Convertir en liste triée de tuples, elle est deja triee si tout va bien.
            # La retrier changerait le plan de vol, c'est une mauvaise idee !!!!
            list_items = list(flight_plan_timed.items())  
            lower, upper = None, None
            for i, (key, value) in enumerate(list_items):
                if time < value:
                    upper = key
                    lower = list_items[i - 1][0] if i > 0 else None
                    break
            else:
                lower = list_items[-1][0]
            return lower, upper
        #---------------------------------------
        self.flight_time = max(0, target_time - self.take_off_time) # si target_time < take_off alors avion pas décollé
        #self.time = target_time
        if target_time < self.take_off_time: # L'avion ne bouge pas
            self._is_finished = False
            self.position = self.start_position
            self.heading  = self.calculate_heading(self.start_position, self.flight_plan[0])
            return self.start_position
        else: # L'avion doit bouger
            # Trouver les balises entre lesquelles se trouve l'avion
            previous_balise_name, next_balise_name = find_keys(flight_plan_timed=self.flight_plan_timed, time=target_time)

            #-------------- Cas 1 --------------------------
            if next_balise_name == None:  # L'avion est arrivé à sa dernière balise
                self._is_finished = True
                x, y = self.flight_plan[-1].get_point().getXY() # se positionner sur la balise
                self.position = Point(x, y, z=self.position.getZ())
                return self.position
            else: # L'avion a une prochaine balise donc recuperation du temps de passage a la balise
                next_balise      = Balise.get_balise_by_name(next_balise_name)
                next_balise_time = self.flight_plan_timed.get(next_balise_name)
            
            #-------------- Cas 2 --------------------------
            if previous_balise_name == None: # L'avion a démarré et est entre sa position_start et la next_balise (1ere)
                previous_balise      = self.start_position
                previous_balise_time = self.take_off_time # L'avion etait au depart si il n'y a pas de balise précédante
            else: # L'avion connait sa balise precedante
                previous_balise       = Balise.get_balise_by_name(previous_balise_name)
                previous_balise_time  = self.flight_plan_timed.get(previous_balise_name)

            # La gestion des cas a ete faite:
            # les différentes variables sont définies et différentes de None
            # Calcul de la fraction du trajet effectuée
            progress = (self.__round(target_time) - previous_balise_time) / (next_balise_time - previous_balise_time)

            # Interpolation linéaire entre les balises
            new_x = previous_balise.getX() + progress * (next_balise.getX() - previous_balise.getX())
            new_y = previous_balise.getY() + progress * (next_balise.getY() - previous_balise.getY())
            new_z = self.position.getZ() #+ progress * (next_balise.getZ() - balise.getZ())

            # Mettre à jour le heading de l'avion
            new_point = Point(new_x, new_y, new_z)
            self.heading = self.calculate_heading(new_point, next_balise)
            self.position = new_point
            self._is_finished = False
            #return self.controle_position(new_x, new_y, new_z) # modifie le heading pour faire un rebond 
            return new_point # raise error si les new_xyz sortent de MinMax Value

    
    def set_next_command(self) -> Optional[DataStorage]:
        "renvoie la prochiane commands a appliqué "
        if not self.commands:  # Si aucune commande n'est définie
            return None

        # Rechercher la première commande dont le temps est supérieur à l'heure actuelle
        next_command = next((cmd for cmd in self.commands if (cmd.time > self.time and cmd.time > self.take_off_time)), None)
        return next_command

    
    def set_commands(self, commands: List[DataStorage], recalcul : bool = True, dt:int = 0) -> None:
        """ Set la liste de commande a l'avion (DataStorage) et recalcule les conflit en consequence"""
        if commands:
            commands.sort(key= lambda c: c.time)
            self.commands = commands
            
            if self.commands:
                cmd = commands[0]
                self.set_take_off_time(cmd.time)
                self.set_speed(cmd.speed)
                #self.set_heading(cmd.heading)

        # Recalculer les conflicts
        self.update_conflicts(recalcul=recalcul, dt=dt)

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

    def __round(self, value: float) -> float:
        return round(value, 2)


class AircraftCollector(Collector[Aircraft]):
    def __init__(self, value: Aircraft = None):
        super().__init__()
        if value: self.add(value)
    
    def add_aircraft(self, value: Aircraft) -> None:
        super().add(key = value.get_id_aircraft(), value=value)