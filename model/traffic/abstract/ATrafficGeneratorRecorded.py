from abc import abstractmethod
from model.traffic.abstract.ATrafficGenerator import ATrafficGenerator
from utils.reader.AReader import AReader
from utils.formatter.AFormat import AFormat
from utils.controller.database_dynamique import MetaDynamiqueDatabase

from model.aircraft.aircraft import Aircraft
from typing import Dict

from typing_extensions import override

import numpy as np

@ATrafficGenerator.register_traffic_generator
class ATrafficGeneratorRecorded(ATrafficGenerator):
    """Générateur statique de trafic aérien nécessitant 3 paramètres:
        - container: str, endroit où est stockée la donnée (nom fichier, nom de la base de donnée).
        - reader: AReader, classe concrète héritant de AReader permettant de lire la donnée depuis le container.
        - parser: AFormat, classe concrète héritant de AFormat permettant de parser le contenu de la donnée (par exemple JSONFormat).
    """

    @abstractmethod
    def __init__(self, reader: AReader, parser: AFormat, **kwargs):
        """
        Constructeur imposant trois paramètres obligatoires.

        :param container: str: Où est stockée la donnée (nom de fichier, nom de la base de donnée)
        :param reader: AReader, classe concrète permettant de lire la donnée depuis le container (par exemple FileReader).
                       Le paramètre ne doit pas être instancié.
        :param parser: AFormat, classe concrète permettant de parser la donnée lue (par exemple JSONFormat).
                       Le paramètre ne doit pas être instancié.
        """
        # Instanciation des classes concrètes
        self.reader: AReader = reader  # Le container est passé au lecteur 
        self.parser: AFormat = parser  # Instancie le parser

        # Appel au constructeur de la classe parente avec les arguments supplémentaires
        super().__init__(**kwargs)

        self.__simulation_duration = None
        self.__generator = None
        self.reset_seed()

    @override
    def generate_traffic(self) -> Dict[int, Aircraft]:
        """Implémentation de la génération de trafic en utilisant le reader et le parser.
        Retourne le dictionnaire Dict[int, Aircraft]"""
        data_str = self.reader.read()  # Utilise le lecteur pour obtenir la chaîne de données
        parsed_data = parsed_data = self.parser.parse(data_str)  # Parse la donnée pour obtenir les avions
        self.__simulation_duration = self.__find_simulation_duration(parsed_data)
        return parsed_data  # Retourne un dictionnaire d'objets Aircraft (ou ce qui est retourné par le parser)

    @override
    def reset_seed(self) -> None:
        """Réintialise la seed du générateur"""
        seed = int(self.__simulation_duration) if self.__simulation_duration else self.__simulation_duration
        self.__generator = np.random.default_rng(seed=seed)
        

    def get_generator(self) -> np.random.Generator:
        """Renvoie le générateur aléatoire"""
        return self.__generator

    @override
    def get_simulation_duration(self) -> float:
        """Renvoie la durée de la simulation en secondes"""
        return self.__simulation_duration
    
    def __find_simulation_duration(self, parsed_data: Dict[int, Aircraft]) -> float:
        # Liste des dernières valeurs des plans de vol de chaque avion
        last_times = [a.get_arrival_time_on_last_point() for a in parsed_data.values()]
        
        # Retourner la durée maximale
        return max(last_times) if last_times else 0.0  # 0.0 si aucune donnée n'est présente