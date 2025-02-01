from model.traffic.abstract.ATrafficGeneratorRecorded import ATrafficGeneratorRecorded
from utils.reader.AReader import AReader
from utils.formatter.AFormat import AFormat

@ATrafficGeneratorRecorded.register_traffic_generator
class TrafficGeneratorRecorded(ATrafficGeneratorRecorded):
    """Générateur statique de trafic aérien nécessitant 3 paramètres:
        - container: str, endroit où est stockée la donnée (nom fichier, nom de la base de donnée).
        - reader: AReader, classe concrète héritant de AReader permettant de lire la donnée depuis le container.
        - parser: AFormat, classe concrète héritant de AFormat permettant de parser le contenu de la donnée (par exemple JSONFormat).
    """
    def __init__(self, reader: AReader, parser: AFormat, **kwargs):
        """
        Constructeur imposant trois paramètres obligatoires.

        :param container: str: Où est stockée la donnée (nom de fichier, nom de la base de donnée)
        :param reader: AReader, classe concrète permettant de lire la donnée depuis le container (par exemple FileReader).
                       Le paramètre ne doit pas être instancié.
        :param parser: AFormat, classe concrète permettant de parser la donnée lue (par exemple JSONFormat).
                       Le paramètre ne doit pas être instancié.
        Exemple:
            traffig_generator = TrafficGeneratorRecorded(container='test.json', 
                                                        reader=FileReader, 
                                                        parser=JSONFormat)

            traffig_generator.generate_traffic()
        """
        super().__init__(reader=reader, parser=parser, **kwargs)
