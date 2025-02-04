from utils.reader.IReader import IReader
from utils.controller.database_dynamique import MetaDynamiqueDatabase

from typing import Type

class AReader(IReader):
    """Classe abstraite pour les lecteurs de données."""

    def __init__(self, source: str):
        super().__init__(source)
        self.source = source

    def get_source(self) -> str:
        """Renvoie la source du fichier"""
        return self.source

    def __repr__(self):
        return f"{self.__class__.__name__}(source='{self.source}')"

    def read(self) -> str:
        """Lit des données et retourne une chaîne formatée."""
        pass

    @classmethod
    def register_reader(cls, reader_class: Type):
        """Classe décoratrice pour enregistrer un nouveau reader.
        Exception TypeError
        """
        reader_class = MetaDynamiqueDatabase.register(subclass=reader_class)
        params = MetaDynamiqueDatabase.get_class_constructor_params(base_class=cls, class_name= reader_class.__name__)
        # Vérifie que le constructeur (init) n'accepte que `self`et la source
        if len(params) != 1: # self est deja retirer dans MetaDynamiqueDatabase
            error =  f"Class {cls.__name__}({cls.__bases__[0]}) shoud have only one parameter (source: str), total parameters:(self, source: str)."
            error += f" source is the string related to where reading will be done (filename or database for example)"
            raise TypeError(error)
        return reader_class


    @classmethod
    def get_available_readers(cls):
        """
        Retourne la liste des noms des readers disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)

    @classmethod
    def discover_readers(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les readers (ex. 'utils.reader').
        """
        return MetaDynamiqueDatabase.discover_dynamic(package=package)

    @classmethod
    def get_reader_class(cls, name: str) -> 'AReader':
        """
        Renvoie une classe AReader à partir de son nom enregistré.
        L'instance n'est pas crée.
        Exception: TypeError ou ValueError
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"Reader '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_reader en décoration de la classe dérivée pour enregistré le reader."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)
    
    @classmethod
    def create_reader(cls, name: str, source: str) -> 'AReader':
        """
        Instancie une classe AReader à partir de son nom enregistré.
        Exception: TypeError ou ValueError
        """
        return cls.get_reader_class(name)(source)
