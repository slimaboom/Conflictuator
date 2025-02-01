from utils.formatter.AFormat import AFormat
from typing import List, Dict
from typing_extensions import override, TYPE_CHECKING

from algorithm.data import DataStorage
from model.aircraft.aircraft import Information
from model.aircraft.aircraft import Aircraft
from model.route import Airway
import json

@AFormat.register_format
class JSONFormat(AFormat):
    """Classe concrète de format JSON"""

    COMMAND_KEY     = "commands"
    HISTORY_KEY     = "history"
    FLIGHT_PLAN_KEY = "flight_plan"
    def __init__(self):
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"
    
    @override
    def export(self, iterable: List['Aircraft']) -> str:
        """
        Exporte les informations d'une List[Aircraft] au format JSON
        avec une structure clé/valeur organisée.
        """
        
        # Sérialisation JSON
        data = {aircraft.get_id_aircraft(): self.__export_one(aircraft) for aircraft in iterable}
        return json.dumps(data, indent=4, default=self.__serialize_command)

    def __export_one(self, obj: 'Aircraft') -> Dict:
        """
        Exporte les informations du plan de vol timé d'un Aircraft sous forme de dictionnaire.
        """
        # Sérialiser les commandes et l'historique pour un seul avion
        commands = obj.get_commands()
        flight_plan_timed = obj.get_flight_plan_timed()

        # Retourner les données sous forme de dictionnaire
        exported = {self.COMMAND_KEY: commands, 
                    self.FLIGHT_PLAN_KEY: flight_plan_timed}
        return exported

    # def __export_one(self, obj: 'Aircraft') -> Dict:
    #     """
    #     Exporte les informations d'un Aircraft sous forme de dictionnaire.
    #     """
    #     # Sérialiser les commandes et l'historique pour un seul avion
    #     commands = [self.__serialize_command(c) for c in obj.get_commands()]
    #     history = {t: self.__serialize_command(info) for t, info in obj.get_history().items()}
    #     flight_plan = obj.get_flight_plan_timed()

    #     # Retourner les données sous forme de dictionnaire
    #     exported = {self.COMMAND_KEY: commands, 
    #                 self.HISTORY_KEY: history, 
    #                 self.FLIGHT_PLAN_KEY: flight_plan}
    #     return exported

    def __serialize_command(self, obj):
        if isinstance(obj, list):
            return [self.__serialize_command(item) for item in obj]  # Sérialise les listes
        elif isinstance(obj, dict):
            return {k: self.__serialize_command(v) for k, v in obj.items()}  # Sérialise les dicts
        else:
            return obj.__dict__  # Retourne l'objet brut en dictionnaire s'il est déjà JSON

    @override
    def parse(self, data: str) -> Dict[int, 'Aircraft']:
        """Renvoie le parsing de l'argument <data> qui est une chaine en un objet List['Aircraft']"""
        data_dict = json.loads(data) # C'est la classe JSONFormat ici donc on peut utiliser le module json
        aircrafts_dict = {}
        for aircraft_id in data_dict:
            aircraft_dict = data_dict.get(aircraft_id) # key: self.***_KEY
            id = int(aircraft_id)
            for type_info in aircraft_dict: # Parcourt des informations
                details = aircraft_dict.get(type_info)
                # Commands
                if type_info == self.COMMAND_KEY:
                    commands = [DataStorage(**cmd) for cmd in details]

                # Historique
                elif type_info == self.HISTORY_KEY:
                    history = [Information.from_dict(info) for _, info in details.items()]
                # Flight Plan Timed
                else:# self.FLIGHT_PLAN_KEY
                    flight_plan_timed = details

            # Creation instance Aircraft enregistres
            aircraft = Aircraft(flight_plan=Airway.transform(list(flight_plan_timed.keys())),
                                speed=commands[0].speed,
                                id=id)
            aircrafts_dict[id] = aircraft
        return aircrafts_dict
