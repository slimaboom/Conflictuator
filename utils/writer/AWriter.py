from abc import abstractmethod
from typing import List, Type
from typing_extensions import override

from utils.controller.database_dynamique import MetaDynamiqueDatabase
from utils.writer.IWriter import IWriter

class AWriter(IWriter):
    """Classe abstraite pour les classes qui écrivent des données"""

    @override
    def __init__(self, container: str):
        """Constructeur avec un seul paramètre correspondant à où l'écriture va se faire (fichier, base de donnée)"""
        super().__init__(container)
        self.__container = container

    def __repr__(self):
        return f"{self.__class__.__name__}(container='{self.__container}')"

    def write(self, text: str) -> bool:
        """Renvoie True si l'écriture du <texte> a été possible et False sinon"""
        pass
    
    def get_container(self) -> str: 
        """Chaine de caractères passée aux constructeur permettant de savoir où la classe écrit (fichier, base de donnée, ect)"""
        return self.__container

    @classmethod
    def register_writer(cls, writer_class: Type):
        """Classe décoratrice pour enregistrer un nouveau writer.
        Exception TypeError
        """
        writer_class = MetaDynamiqueDatabase.register(subclass=writer_class)
        params = MetaDynamiqueDatabase.get_class_constructor_params(base_class=cls, class_name=writer_class.__name__)
        # Vérifie que le constructeur (init) n'accepte que `self` et le container
        if len(params) != 1: # self est deja retirer dans MetaDynamiqueDatabase
            error =  f"Class {cls.__name__}({cls.__bases__[0]}) shoud have only one parameter (container: str), total parameters:(self, container: str)."
            error += f" container is the string related to where writting will be done (filename or database for example)"
            raise TypeError(error)
        return writer_class


    @classmethod
    def get_available_writers(cls):
        """
        Retourne la liste des noms des writers disponibles.
        Exception: TypeError
        """
        return MetaDynamiqueDatabase.get_available(base_class=cls)


    @classmethod
    def discover_writers(cls, package: str):
        """
        Découvre et importe tous les modules dans un package donné.
        
        :param package: Le chemin du package où chercher les writers (ex. 'utils.writer').
        """
        return MetaDynamiqueDatabase.discover_dynamic(package=package)


    @classmethod
    def get_writer_class(cls, name: str) -> 'AWriter':
        """
        Renvoie une classe AWriter à partir de son nom enregistré.
        L'instance n'est pas crée.
        Exception: TypeError ou ValueError
        """
        try:
            return MetaDynamiqueDatabase.get_class(base_class=cls, name=name)
        except Exception as e:
            error = f"Writer '{name}' non supporté car non enregistré dans la classe {cls.__name__}"
            error += f"\nUtiliser @{cls.__name__}.register_writer en décoration de la classe dérivée pour enregistré le writer."
            full_message = f"{str(e)}\n{error}"
            raise type(e)(full_message)


    @classmethod
    def create_writer(cls, name: str, container: str) -> 'AWriter':
        """
        Instancie une classe AWriter à partir de son nom enregistré, et du container
        Exception: TypeError ou ValueError
        """
        return cls.get_writer_class(name)(container)
