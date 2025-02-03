from abc import abstractmethod
from typing import List, Type, TYPE_CHECKING, Dict

from utils.formatter.IFormat import IFormat
from utils.controller.database_dynamique import MetaDynamiqueDatabase

if TYPE_CHECKING:
    from model.aircraft.aircraft import Aircraft

class AFormat(IFormat):
    """Class abstraites pour les formats de données gérant une base de données des différents formats disponibles"""

    def __init__(self):
        pass

    @abstractmethod
    def export(self, iterable: List['Aircraft']) -> str:
        """Renvoie l'export de la liste des Aircraft dans une chaine de caractère correspond au format souhaité"""
        pass

    @abstractmethod
    def parse(self, data: str) -> Dict[int, 'Aircraft']:
        """Renvoie le parsing de l'argument <data> qui est une chaine en un objet List['Aircraft']"""
        pass

    @classmethod
    def register_format(cls, format_class: Type):
        """Classe décoratrice pour enregistrer un nouveau format.
        Exception TypeError
        """
        format_class = MetaDynamiqueDatabase.register(subclass=format_class)
        params = MetaDynamiqueDatabase.get_class_constructor_params(base_class=cls, class_name= format_class.__name__)
        # Vérifie que le constructeur (init) n'accepte que `self`
        if len(params) != 0: # self est deja retirer dans MetaDynamiqueDatabase
            error =  f"Class {cls.__name__}({cls.__bases__[0]}) should not have 0 parameter to instanciate the class except (self)"
            raise TypeError(error)
        return format_class


    @classmethod
    def get_available_formats(cls):
        """
        Retourne la liste des noms des formats disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)

    @classmethod
    def discover_formatters(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les formats (ex. 'utils.formatter').
        """
        return MetaDynamiqueDatabase.discover_dynamic(package=package)

    @classmethod
    def get_format_class(cls, name: str) -> 'AFormat':
        """
        Renvoie une classe AFormat à partir de son nom enregistré.
        L'instance n'est pas crée.
        Exception: TypeError ou ValueError
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"Format '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_format en décoration de la classe dérivée pour enregistré le format."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)
    
    @classmethod
    def create_formatter(cls, name: str) -> 'AFormat':
        """
        Instancie une classe AFormat à partir de son nom enregistré.
        Exception: TypeError ou ValueError
        """
        return cls.get_format_class(name)()
