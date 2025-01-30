
from dataclasses import dataclass
from model.point import Point
from utils.conversion import rad_to_deg_aero


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

    @classmethod
    def from_dict(cls, data: dict):
        """Crée une instance d'Information à partir d'un dictionnaire, 
        transformant la position en un objet Point.
        """
        key_pos = 'position'
        position_data = data.pop(key_pos, {})  # Récupère la position et la retire du dict
        position = Point(**position_data)  # Crée l'objet Point à partir des coordonnées
        data[key_pos] = position
        return cls(**data)