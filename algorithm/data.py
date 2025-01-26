from algorithm.interface.ISimulatedObject import VariableName, ASimulatedAircraft
from model.aircraft import Aircraft, SpeedValue
from algorithm.storage import DataStorage
from typing import List
from typing_extensions import override
from logging_config import setup_logging

import numpy as np

class SimulatedAircraftImplemented(ASimulatedAircraft):
    """Implémentation concrète de ASimulatedAircraft"""
    PRECISION           = 4
    NB_MAXIMUM_COMMANDS = 5
    NB_SPEEDS_POSSIBLE  = 20

    @override
    def __init__(self, aircraft: Aircraft):
        """Constructeur obligeant à passer un avion en parametre."""
        self.logger = setup_logging(self.__class__.__name__)

        super().__init__(aircraft)

        self.__aircraft = self.get_object()
        self.__random_generator = aircraft.get_random_generator()
        self.__possible_speeds  = [0.001, 0.002, 0.003, 0.0012] #np.round(np.linspace(SpeedValue.MIN.value, SpeedValue.MAX.value, self.NB_SPEEDS_POSSIBLE), self.PRECISION)
        
        self.__commands = aircraft.get_commands()
       # self.update_commands(commands=self.initialize())
    
    @override
    def update_commands(self, commands: List[DataStorage]) -> None:
        """Met a jour les commandes pour l'avion"""
        self.__aircraft.set_commands(commands=commands)
        self.__commands = commands
    
    @override
    def initialize(self) -> List[DataStorage]:
        """Initialise les commandes aleatoirement pour l'objet mais ne met pas a jour l'objet"""
        # Générer la première commande : temps de départ et vitesse initiale
        random_takeoff = self.__generate_random_time(low=0., high=180.)
        departure_time = round(max(self.__aircraft.get_take_off_time() + random_takeoff, 0.0) , 2)
        initial_speed =  self.__generate_random_speed()
        
        cmds = [DataStorage(id=self.__aircraft.get_id_aircraft(),
                            time=departure_time,
                            speed=initial_speed,
                            heading=self.__aircraft.get_heading())
                ]
        # Générer les autres commandes
        current_time = departure_time
        num_commands = self.__random_generator.integers(1, self.NB_MAXIMUM_COMMANDS) # Au moins un changement
        for _ in range(num_commands):
            speed = self.__generate_random_speed()
            random_time = self.__generate_random_time(low=0., high=120.)
            time = round(current_time + random_time, 2)

            # DataStorage
            ds = DataStorage(id=self.__aircraft.get_id_aircraft(),
                             time=time,
                             speed=speed,
                             heading=self.__aircraft.get_heading())
            cmds.append(ds)
            current_time = time

        # Liste des changements ordonnée dans le temps
        cmds.sort(key=lambda ds: ds.time)
        return cmds
    
    @override
    def generate_neighbor(self) -> None:
        """Génère un voisin pour l'objet dans l'algorithme"""
        # Exemple d'une nouvelle commande
        new_commands = self.generate_commands()
        self.update_commands(new_commands)
    
    @override
    def get_data_storages(self) -> List[DataStorage]:
        """Storage des donnees de l'objet necessaire lors de l'algorithme"""
        return self.__commands

    @override
    def __repr__(self):
        """Representation de l'objet dans le contexte"""
        return f"Aircraft(id={self.__aircraft.get_id_aircraft()}, commands={self.__aircraft.get_commands()})"
    
        
    def __generate_random_time(self, low: float, high: float) -> float:
        """Genere un temps aleatoire entre [low, high[ ou [low, high] dependant de l'arrondi"""
        return self.__random_generator.uniform(low, high)

    def __generate_random_speed(self) -> float:
        """Genere une vitesse aleatoire dans la liste des vitesses definie en attribut de la classe"""
        return round(self.__random_generator.choice(self.__possible_speeds), self.PRECISION)

    @override
    def generate_commands(self) -> List[DataStorage]:
        """Renvoie une liste de DataStorage tiree aleatoirement representant les commandes de l'avion"""
        if not self.__commands: # Vérifie si des commandes existent
            return self.initialize()
        
        # Détermine le nombre maximum de commandes à modifier
        max_changes = min(len(self.__commands), self.NB_MAXIMUM_COMMANDS)

        # Nombre de commandes à modifier (au moins 1, jusqu'à max_changes)
        num_changes = self.__random_generator.integers(1, max_changes)

        # Sélectionne aléatoirement les indices des commandes à modifier
        indexis = self.__random_generator.integers(0, max_changes, size=num_changes)
        for i in indexis:
            # Selectionne la commande à modifier
            cmd = self.__commands[i]
            
            # Selectionne le nombre de variable à modifier dans la commande
            num_vars_to_change = self.__random_generator.integers(1, 2+1) #3 exclu

            variables = list(VariableName)
            if num_vars_to_change >= len(variables):
                vars_to_change = variables
            else:
                vars_to_change = self.__random_generator.choice(variables, size=num_vars_to_change)

            # Chaque variable à modifier
            time, speed, heading = cmd.time, cmd.speed, cmd.heading
            for var in vars_to_change:
                # Selectionne quelle variable
                if var == VariableName.SPEED:
                    speed = self.__generate_random_speed()  # Nouvelle vitesse initiale
                elif var == VariableName.TIME:
                    if i == 0: # Premiere commande : ajustement du temps de depart
                        # Ajustement si proba de tirer uniforme entre 0 et 1 < 0.1
                        if self.__random_generator.random() < 0.1:
                            random_time = self.__generate_random_time(low=-25.0, high=25.0)
                            time = max(cmd.time + random_time, 0.) # Temps de départ ajusté
                    else:
                        random_time = self.__generate_random_time(low=-10.0, high=10.0)
                        time = max(cmd.time + random_time, 0.) # Temps de commande ajusté                   
                else: # VariableName.HEADING
                    # TO IMPLEMENT
                    continue
            # Modifie la commande dans la liste
            self.__commands[i] = DataStorage(id=self.__commands[i].id, 
                                            speed=speed,
                                            time=time,
                                            heading=heading)
        return self.__commands