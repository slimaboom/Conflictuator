from utils.formatter.AFormat import AFormat
from typing_extensions import override, TYPE_CHECKING

import json

if TYPE_CHECKING:
    from model.aircraft import Aircraft

class JSONAircraftFormat(AFormat):
    @override
    def export(self, obj: 'Aircraft') -> str:
        """
        Exporte les informations d'un Aircraft au format JSON
        avec une structure clé/valeur organisée.
        """
        # Sérialiser les commandes et l'historique
        commands = [self._serialize_command(c) for c in obj.get_commands()]
        history = {t: self._serialize_command(info) for t, info in obj.get_history().items()}

        # Construire la structure JSON
        data = {
            obj.get_id_aircraft(): {  # Identifiant unique de l'avion
                "commands": commands,
                "history": history
            }
        }

        # Sérialisation JSON
        return json.dumps(data, indent=4, default=self._serialize_command)


    def _serialize_command(self, obj):
        if isinstance(obj, list):
            return [self._serialize_command(item) for item in obj]  # Sérialise les listes
        elif isinstance(obj, dict):
            return {k: self._serialize_command(v) for k, v in obj.items()}  # Sérialise les dicts
        else:
            return obj.__dict__  # Retourne l'objet brut en dictionnaire s'il est déjà JSON
