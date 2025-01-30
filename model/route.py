from model.balise import Balise
from typing import List, Dict

class Airway:
    __registry = {}

    def __init__(self, name: str, points: List[str]):
        self.__name   = name
        self.__points = points

        # Enregistrer l'airway dans le registre
        if name:
            if name in self.__registry:
                error = f"{self.__class__.__name__} with name {name} already exists in the registry of {self.__class__.__name__}"
                raise ValueError(error)
            self.__registry[name] = self

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.__name}, points={self.__points})"

    def get_name(self) -> str:
        return self.__name

    def get_points(self) -> List['str']:
        return self.__points
    
    def get_transform_points(self) -> List['Balise']:
        return Airway.transform(routes=self.get_points())

    def get_start_balise_name(self) -> str:
        return self.__points[0]
    
    def get_end_balise_name(self) -> str:
        return self.__points[-1]
    
    @classmethod
    def get_available_airways(cls) -> Dict[str, 'Airway']:
        """Retourne toutes les airways enregistrées."""
        return cls.__registry

    @classmethod
    def get_airway_by_name(cls, name: str) -> 'Airway':
        """Retourne une airway par son nom."""
        return cls.__registry.get(name)
    
    @classmethod
    def transform(cls, routes: List[str], reverse: bool=False) -> List['Balise']:
        converted = [Balise.get_balise_by_name(name) for name in routes]
        if reverse:
            converted = list(reversed(converted))
        return converted