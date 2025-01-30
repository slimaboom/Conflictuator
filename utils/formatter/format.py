from utils.formatter.AFormat import AFormat
from typing import List, Dict
from typing_extensions import override, TYPE_CHECKING

import json

if TYPE_CHECKING:
    from model.aircraft import Aircraft

@AFormat.register_format
class JSONFormat(AFormat):
    """Classe concrète de format JSON"""
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
        Exporte les informations d'un Aircraft sous forme de dictionnaire.
        """
        # Sérialiser les commandes et l'historique pour un seul avion
        commands = [self.__serialize_command(c) for c in obj.get_commands()]
        history = {t: self.__serialize_command(info) for t, info in obj.get_history().items()}
        flight_plan = obj.get_flight_plan_timed()

        # Retourner les données sous forme de dictionnaire
        exported = { "commands": commands, "history": history, 'flight_plan': flight_plan}
        return exported


    def __serialize_command(self, obj):
        if isinstance(obj, list):
            return [self.__serialize_command(item) for item in obj]  # Sérialise les listes
        elif isinstance(obj, dict):
            return {k: self.__serialize_command(v) for k, v in obj.items()}  # Sérialise les dicts
        else:
            return obj.__dict__  # Retourne l'objet brut en dictionnaire s'il est déjà JSON
